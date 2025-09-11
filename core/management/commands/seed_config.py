from django.core.management.base import BaseCommand
from core.models import Configuration

class Command(BaseCommand):
    help = "Seed initial configuration values into the Configuration table."

    CONFIGS = [
        {"config": "enable-cart", "value": "True"},
        {"config": "enable-gpay", "value": "True"},
        {"config": "enable-phonepay", "value": "True"},
        {"config": "enable-emailotp", "value": "True"},
        {"config": "enable-smsotp", "value": "False"},
        {"config": "order-management", "value": "False"},
        {"config": "packages-mode", "value": "True"},
        {"config": "product-management", "value": "False"},
        {"config": "shipping-module", "value": "True"},
        {"config": "show-products-homepage", "value": "True"},
        {"config": "show-testimonial-homepage", "value": "True"},
        {"config": "tax-module", "value": "True"},
    ]

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for item in self.CONFIGS:
            obj, created = Configuration.objects.update_or_create(
                config=item["config"],
                defaults={"value": item["value"]}
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Seeding completed: {created_count} created, {updated_count} updated."
        ))
