from django.db import models

# ================================
# ALL CONVERTED TO TextChoices
# ================================

class StaffRoleChoice(models.TextChoices):
    ADMIN = 'Admin', 'Admin'
    MANAGER = 'Manager', 'Manager'
    EMPLOYEE = 'Employee', 'Employee'
    VENDOR_ADMIN = 'Vendor_Admin', 'Vendor Admin'
    CUSTOMER = 'Customer', 'Customer'
    MEMBER = 'Member', 'Member'
    TRAINER = 'Trainer', 'Trainer'

class GenderChoice(models.TextChoices):
    MALE = 'male', 'Male'
    FEMALE = 'female', 'Female'
    OTHER = 'other', 'Other'

class CountryChoice(models.TextChoices):
    AF = 'AF', 'Afghanistan'
    AL = 'AL', 'Albania'
    DZ = 'DZ', 'Algeria'
    AR = 'AR', 'Argentina'
    AU = 'AU', 'Australia'
    AT = 'AT', 'Austria'
    BD = 'BD', 'Bangladesh'
    BE = 'BE', 'Belgium'
    BR = 'BR', 'Brazil'
    CA = 'CA', 'Canada'
    CN = 'CN', 'China'
    CO = 'CO', 'Colombia'
    DK = 'DK', 'Denmark'
    EG = 'EG', 'Egypt'
    FI = 'FI', 'Finland'
    FR = 'FR', 'France'
    DE = 'DE', 'Germany'
    GH = 'GH', 'Ghana'
    GR = 'GR', 'Greece'
    IN = 'IN', 'India'
    ID = 'ID', 'Indonesia'
    IE = 'IE', 'Ireland'
    IT = 'IT', 'Italy'
    JP = 'JP', 'Japan'
    KE = 'KE', 'Kenya'
    MY = 'MY', 'Malaysia'
    MX = 'MX', 'Mexico'
    NL = 'NL', 'Netherlands'
    NG = 'NG', 'Nigeria'
    NO = 'NO', 'Norway'
    PK = 'PK', 'Pakistan'
    PH = 'PH', 'Philippines'
    PL = 'PL', 'Poland'
    PT = 'PT', 'Portugal'
    RU = 'RU', 'Russia'
    SA = 'SA', 'Saudi Arabia'
    SG = 'SG', 'Singapore'
    ZA = 'ZA', 'South Africa'
    KR = 'KR', 'South Korea'
    ES = 'ES', 'Spain'
    LK = 'LK', 'Sri Lanka'
    SE = 'SE', 'Sweden'
    CH = 'CH', 'Switzerland'
    TH = 'TH', 'Thailand'
    TR = 'TR', 'Turkey'
    UA = 'UA', 'Ukraine'
    AE = 'AE', 'United Arab Emirates'
    GB = 'GB', 'United Kingdom'
    US = 'US', 'United States'
    VN = 'VN', 'Vietnam'

class SocialMediaChoice(models.TextChoices):
    GMAIL = 'GMAIL', 'Gmail'
    FACEBOOK = 'FACEBOOK', 'Facebook'
    INSTAGRAM = 'INSTAGRAM', 'Instagram'
    LINKEDIN = 'LINKEDIN', 'LinkedIn'
    PHONE = 'PHONE', 'Phone'
    TWITTER = 'TWITTER', 'Twitter'
    YOUTUBE = 'YOUTUBE', 'YouTube'
    WHATSAPP = 'WHATSAPP', 'WhatsApp'
    HOME_PAGE_WHATSAPP = 'HOME_PAGE_WHATSAPP', 'Home Page WhatsApp'
    HOME_PAGE_PHONE = 'HOME_PAGE_PHONE', 'Home Page Phone'
    HOME_PAGE_INSTAGRAM = 'HOME_PAGE_INSTAGRAM', 'Home Page Instagram'
    HOME_PAGE_GMAIL = 'HOME_PAGE_GMAIL', 'Home Page Gmail'

class AlertTypeChoice(models.TextChoices):
    SUBSCRIPTION_EXPIRED = 'subscription_expired', 'Subscription Expired'
    SUBSCRIPTION_REMINDER = 'subscription_reminder', 'Subscription Reminder'
    GENERAL = 'general', 'General Alert'

class SessionStatusChoice(models.TextChoices):
    UPCOMING = 'upcoming', 'Upcoming'
    LIVE = 'live', 'Live'
    ENDED = 'ended', 'Ended'

class AttendanceStatusChoice(models.TextChoices):
    CHECKED_IN = 'checked_in', 'Checked In'
    CHECKED_OUT = 'checked_out', 'Checked Out'
    AUTO_CHECKED_OUT = 'auto_checked_out', 'Auto Checked Out'

class GoalChoice(models.TextChoices):
    WEIGHT_LOSS = 'weight_loss', 'Weight Loss'
    WEIGHT_GAIN = 'weight_gain', 'Weight Gain'
    COMPETITION = 'competition', 'Competition'
    BASIC_MAINTENANCE = 'basic_maintenance', 'Basic Maintenance'

class LevelChoice(models.TextChoices):
    BEGINNER = 'beginner', 'Beginner'
    MEDIUM = 'medium', 'Medium'
    ADVANCED = 'advanced', 'Advanced'
    MASTER = 'master', 'Master'

class WeekdayChoice(models.TextChoices):
    MONDAY = 'monday', 'Monday'
    TUESDAY = 'tuesday', 'Tuesday'
    WEDNESDAY = 'wednesday', 'Wednesday'
    THURSDAY = 'thursday', 'Thursday'
    FRIDAY = 'friday', 'Friday'
    SATURDAY = 'saturday', 'Saturday'
    SUNDAY = 'sunday', 'Sunday'

class ActivityTypeChoice(models.TextChoices):
    EXERCISE = 'exercise', 'Exercise'
    CARDIO = 'cardio', 'Cardio'
    CIRCUIT = 'circuit', 'Circuit'
    REST = 'rest', 'Rest'

class WorkoutStatusChoice(models.TextChoices):
    ASSIGNED = 'assigned', 'Assigned'
    ACTIVE = 'active', 'Active'
    COMPLETED = 'completed', 'Completed'
    PAUSED = 'paused', 'Paused'

class PackageTypeChoice(models.TextChoices):
    MONTHLY = 'monthly', 'Monthly'
    QUARTERLY = 'quarterly', 'Quarterly'
    YEARLY = 'yearly', 'Yearly'
    CUSTOM = 'custom', 'Custom'

class DiscountTypeChoice(models.TextChoices):
    NONE = 'none', 'None'
    FLAT = 'flat', 'Flat Amount'
    PERCENT = 'percent', 'Percentage'

class PaymentActionChoice(models.TextChoices):
    INITIATE = 'INITIATE', 'Initiate Payment'
    FETCH_SESSION = 'FETCH_SESSION', 'Fetch Session'
    GET_ORDER = 'GET_ORDER', 'Get Existing Order'
    CREATE_LINK = 'CREATE_LINK', 'Create Payment Link'
    WEBHOOK = 'WEBHOOK', 'Webhook'
    ERROR = 'ERROR', 'Error'  # ✅ FIXED SYNTAX

class TransactionTypeChoice(models.TextChoices):
    INCOME = 'income', 'Income'
    EXPENSE = 'expense', 'Expense'

class TransactionCategoryChoice(models.TextChoices):
    SALES = 'sales', 'Sales'
    REFUND = 'refund', 'Refund'
    SALARY = 'salary', 'Salary'
    RENT = 'rent', 'Rent'
    UTILITIES = 'utilities', 'Utilities'
    MARKETING = 'marketing', 'Marketing'
    INVENTORY = 'inventory', 'Inventory'
    OTHER = 'other', 'Other'

class TransactionStatusChoice(models.TextChoices):
    INITIATED = 'initiated', 'Initiated'
    PENDING = 'pending', 'Pending'
    COMPLETED = 'completed', 'Completed'
    REFUNDED = 'refunded', 'Refunded'

class PaymentStatusChoice(models.TextChoices):
    PENDING = 'pending', 'Pending'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    REFUNDED = 'refunded', 'Refunded'


class TicketStatusChoice(models.TextChoices):
    OPEN = 'open', 'Open'
    IN_PROGRESS = 'in_progress', 'In Progress'
    RESOLVED = 'resolved', 'Resolved'
    CLOSED = 'closed', 'Closed'

class EnquiryStatusChoice(models.TextChoices):
    NEW = 'new', 'New'
    CONTACTED = 'contacted', 'Contacted'
    IN_PROGRESS = 'in_progress', 'In Progress'
    RESOLVED = 'resolved', 'Resolved'
    CLOSED = 'closed', 'Closed'


class SubscriptionStatusChoice(models.TextChoices):
    PENDING = 'pending', 'Pending'
    ACTIVE = 'active', 'Active'
    EXPIRED = 'expired', 'Expired'
    CANCELLED = 'cancelled', 'Cancelled'

class DriverStatusChoice(models.TextChoices):
    AVAILABLE = 'available', 'Available'
    BUSY = 'busy', 'Busy'
    OFFLINE = 'offline', 'Offline'  

class RideStatusChoice(models.TextChoices):
    REQUESTED = 'requested', 'Requested'
    ACCEPTED = 'accepted', 'Accepted'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'

class VehicleTypeChoice(models.TextChoices):
    BIKE = 'bike', 'Bike'
    SCOOTER = 'scooter', 'Scooter'
    BICYCLE = 'bicycle', 'Bicycle'
    CAR = 'car', 'Car'



class CustomerAddressTypeChoice(models.TextChoices):
    HOME = 'home', 'Home'
    WORK = 'work', 'Work'
    OTHER = 'other', 'Other'


class OrderStatusChoice(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    PREPARING = 'preparing', 'Preparing'
    READY_FOR_PICKUP = 'ready_for_pickup', 'Ready for Pickup'
    ASSIGNED_RIDER = 'assigned_rider', 'Assigned to Rider'
    PICKED_UP = 'picked_up', 'Picked Up'
    OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for Delivery'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'
    REFUNDED = 'refunded', 'Refunded'


class PaymentMethodChoice(models.TextChoices):
    COD = 'cod', 'Cash on Delivery'
    ONLINE = 'online', 'Online Payment'
    WALLET = 'wallet', 'Wallet'



class ReviewTypeChoice(models.TextChoices):
    PRODUCT = 'product', 'Product Review'
    VENDOR = 'vendor', 'Vendor Review'
    RIDER = 'rider', 'Rider Review'