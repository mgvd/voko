from braces.views import LoginRequiredMixin

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, FormView, View, UpdateView
from django.views.generic.detail import SingleObjectMixin
from log import log_event

from ordering.core import get_or_create_order, get_order_product, update_totals_for_products_with_max_order_amounts

from ordering.forms import OrderProductForm
from ordering.mixins import UserOwnsObjectMixin
from ordering.models import Product, OrderProduct, Order, Supplier, OrderRound, ProductCategory


class ProductsView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        order_round = self.request.current_order_round

        # Manual override to show product list of specific round
        if 'round' in self.request.GET:
            order_round = OrderRound.objects.get(id=int(self.request.GET.get('round')))

        return Product.objects.filter(order_round=order_round).order_by('name')

    def get(self, *args, **kwargs):
        ret = super(ProductsView, self).get(*args, **kwargs)
        order = get_or_create_order(self.request.user)
        if order.finalized is True:
            messages.warning(self.request, "Je bent doorgestuurd naar de betaalpagina omdat je bestelling nog niet is betaald!")
            return HttpResponseRedirect(reverse('finance.choosebank'))
        return ret

    def post(self, request, *args, **kwargs):
        """
        Handling complex forms using Django's forms framework is nearly impossible without
         all kinds of trickery that don't necessarily make the code more readable. Hence: manual parsing of POST data.
        """
        order = get_or_create_order(self.request.user)
        assert order.finalized is False
        assert order.paid is False

        for key, value in request.POST.iteritems():
            if key.startswith("order-product-") and (value.isdigit() or value == ""):
                try:
                    prod_id = int(key.split("-")[-1])
                    value = value.strip()
                except (IndexError, ValueError):
                    messages.add_message(self.request, messages.ERROR,
                                         "Er ging iets fout bij het opslaan. "
                                         "Probeer het opnieuw of neem contact met ons op.")
                    return redirect('view_products')

                product = Product.objects.get(id=prod_id)
                try:
                    order_product = OrderProduct.objects.get(order=order, product=product)
                except OrderProduct.DoesNotExist:
                    order_product = None

                if value.isdigit() and product.maximum_total_order and int(value) > product.amount_available:
                    if product.is_available:
                        messages.add_message(self.request, messages.ERROR,
                                             "Van het product '%s' van %s is nog %s %s beschikbaar!"
                                             % (product.name, product.supplier.name, product.amount_available,
                                                product.unit_of_measurement.lower()))
                    else:
                        messages.add_message(self.request, messages.ERROR, "Het product '%s' van %s is uitverkocht!"
                                             % (product.name, product.supplier.name))
                    value = 0

                # User deleted a product
                if type(value) != int and not value.isdigit():
                    value = 0
                if not int(value):
                    if order_product:
                        order_product.delete()
                    continue

                # Update orderproduct
                if order_product:
                    if order_product.amount != int(value):
                        order_product.amount = int(value)
                        order_product.save()

                    continue

                # Create orderproduct
                if value and int(value) > 0:
                    OrderProduct.objects.create(order=order, product=product, amount=int(value))

        return redirect(reverse('finish_order', args=(order.pk,)))

    def get_context_data(self, **kwargs):
        context = super(ProductsView, self).get_context_data(**kwargs)
        context['current_order_round'] = self.request.current_order_round

        # Manual override to show product list of specific round
        if 'round' in self.request.GET:
            context['current_order_round'] = OrderRound.objects.get(id=int(self.request.GET.get('round')))

        context['order'] = get_or_create_order(self.request.user)
        return context

    def order_products(self):
        order = get_or_create_order(self.request.user)
        return order.orderproducts.all().select_related()

    def products(self):
        order = get_or_create_order(self.request.user)
        qs = self.get_queryset()
        for prod in qs:
            if prod.orderproducts.filter(order=order):
                prod.ordered_amount = prod.orderproducts.get(order=order).amount
        return qs

    def categories(self):
        return ProductCategory.objects.all().order_by('name')

    def suppliers(self):
        return Supplier.objects.all()


class ProductDetail(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        view = ProductDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ProductOrder.as_view()
        return view(request, *args, **kwargs)


class ProductDisplay(LoginRequiredMixin, DetailView):
    model = Product

    def _get_initial(self):
        order = get_or_create_order(self.request.user)
        return {'product': self.get_object().pk,
                'order': order.pk}

    def form(self):
        existing_op = get_order_product(product=self.get_object(),
                                        order=get_or_create_order(self.request.user))
        return OrderProductForm(initial=self._get_initial(), instance=existing_op)


class ProductOrder(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = Product
    form_class = OrderProductForm

    def get_success_url(self):
        return reverse("finish_order", kwargs={'pk': get_or_create_order(self.request.user).pk})

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = form_class(request.POST, instance=get_order_product(product=self.get_object(),
                                                                   order=get_or_create_order(
                                                                       user=self.request.user
                                                                   )))
        if form.is_valid():
            order = get_or_create_order(request.user)
            assert order.finalized is False
            assert order.paid is False

            order_product = form.save(commit=False)
            order_product.order = order
            assert order_product.product.order_round == self.request.current_order_round  # TODO: nicer error, or just disable ordering.

            # Remove product from order when amount is zero
            if order_product.amount < 1:
                if order_product.id is not None:
                    order_product.delete()
                return self.form_valid(form)

            order_product.save()
        return self.form_valid(form)


class FinishOrder(LoginRequiredMixin, UserOwnsObjectMixin, UpdateView):
    template_name = "ordering/order_finish.html"
    model = Order

    def get_queryset(self):
        qs = super(FinishOrder, self).get_queryset()
        return qs.filter(paid=False)

    def get_context_data(self, **kwargs):
        update_totals_for_products_with_max_order_amounts(self.get_object())
        return super(UpdateView, self).get_context_data(**kwargs)

    def calculate_payment(self):
        order = self.get_object()
        return order.total_price_to_pay_with_balances_taken_into_account()

    def post(self, request, *args, **kwargs):
        order = self.get_object()

        user_notes = request.POST.get('notes').strip()
        if user_notes:
            order.user_notes = user_notes

        log_event(event="Finalizing order %s" % order.id, user=order.user)
        order.finalized = True  # Freeze order
        order.save()

        if self.calculate_payment() == 0:
            log_event(event="Payment for order %d not necessary because order total is %f and user's credit is %f" %
                            (order.id, order.total_price, order.user.balance.credit()), user=order.user)
            messages.add_message(self.request, messages.SUCCESS,
                                 'Omdat je genoeg krediet had was betalen niet nodig. '
                                 'Je bestelling is bevestigd.')
            order.complete_after_payment()
            return redirect(reverse('order_summary', args=(order.pk,)))

        # Store order_id in session
        request.session['order_to_pay'] = order.id
        return redirect('finance.choosebank')


class OrdersDisplay(LoginRequiredMixin, UserOwnsObjectMixin, ListView):
    """
    Overview of multiple orders
    """
    def get_queryset(self):
        return self.request.user.orders.all().order_by("-pk")


class OrderSummary(LoginRequiredMixin, UserOwnsObjectMixin, UpdateView):
    template_name = "ordering/order_summary.html"
    model = Order

    def get_queryset(self):
        qs = super(OrderSummary, self).get_queryset()
        return qs.filter(paid=True)


class SupplierView(LoginRequiredMixin, DetailView):
    model = Supplier


