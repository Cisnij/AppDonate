from .env_config import env,SECRET_KEY,DEBUG

SITE_ID = 2

REST_FRAMEWORK = {  # Cấu hình token

    'DEFAULT_RENDERER_CLASSES': (

        'drf_orjson_renderer.renderers.ORJSONRenderer',  # dùng orjson để response nhanh hơn vì viết bằng rust

    ),

    'DEFAULT_AUTHENTICATION_CLASSES': [

        'rest_framework_simplejwt.authentication.JWTAuthentication',  # xác thực jwt

        'rest_framework.authentication.SessionAuthentication',  # xác thực cho web

    ],

    'DEFAULT_THROTTLE_CLASSES': [  # Chống spam và bruteforce của rest framework

        'rest_framework.throttling.ScopedRateThrottle',

        # khai báo throttle mặc đinh cho khách và user

        # 'rest_framework.throttling.AnonRateThrottle', # Chống quét cho khách

        # 'rest_framework.throttling.UserRateThrottle', # Chống quét cho user đã login

    ],

    'DEFAULT_THROTTLE_RATES': {
    },

    "DEFAULT_PARSER_CLASSES": [  # dùng cho phép nhận nhiều định dạng dữ liệu khác nhau

        'drf_orjson_renderer.parsers.ORJSONParser',  # dungg orjson để chuyển qua json qua python nhanh hơn khi input

        "rest_framework.parsers.JSONParser",

        "rest_framework.parsers.FormParser",

        "rest_framework.parsers.MultiPartParser",

    ]

}
REST_AUTH={ #Đăng kí trả về json

    'USE_JWT':True,

    'VERIFY_EMAIL_SERIALIZER': 'dj_rest_auth.registration.serializers.VerifyEmailSerializer',

    'CONFIRM_EMAIL_SERIALIZER': 'dj_rest_auth.registration.serializers.ConfirmEmailSerializer',

    'PASSWORD_RESET_SERIALIZER': 'dj_rest_auth.serializers.PasswordResetSerializer',

    'PASSWORD_RESET_CONFIRM_SERIALIZER': 'dj_rest_auth.serializers.PasswordResetConfirmSerializer',

    'PASSWORD_CHANGE_SERIALIZER': 'dj_rest_auth.serializers.PasswordChangeSerializer',

    'USER_DETAILS_SERIALIZER':'dj_rest_auth.serializers.UserDetailsSerializer',

    'REGISTER_SERIALIZER': 'custome_authen.custome_authen.CustomRegisterSerializer',#bên serializers.py

    'LOGOUT_ON_PASSWORD_CHANGE':True, #logout khi change pass

    'TOKEN_MODEL': None,

    'OLD_PASSWORD_FIELD_ENABLED' : True, # Phải nhập mk cũ mới đc đổi mk

    'LOGIN_SERIALIZER': 'custome_authen.custome_authen.CustomeLoginSerializer',#bên serializers.py

    'JWT_AUTH_HTTPONLY' : False #Nếu dùng cho mobile thì false để trả vể refresh token, chỉ dùng web thì nên true để bảo mật, nhưng đã custome cho web riêng nên để false

    #JWT_AUTH_COOKIE và JWT_AUTH_REFRESH_COOKIE sẽ được sử dụng nếu bạn muốn lưu token trong cookie web và k trả về json

}
from datetime import timedelta

SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),

    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": True,
    # có nghĩa là nếu hoạt động tiếp tục thì sẽ chưa bị đăng nhập lại để làm mới refresh token, chỉ khi nào tính từ lúc off 7 ngày mới phải đăng nhập lại

    "BLACKLIST_AFTER_ROTATION": True,

    "ALGORITHM": "HS256",

    "SIGNING_KEY": SECRET_KEY,

    "AUTH_HEADER_TYPES": ("Bearer",),

    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",

    "USER_ID_FIELD": "id",

    "USER_ID_CLAIM": "user_id",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),

    "TOKEN_TYPE_CLAIM": "token_type",

}

#Vào trang này tạo password để google gửi mail https://myaccount.google.com/apppasswords?rapt=AEjHL4OhamB7RBkSZ38jKPnEu25PBC4T4-xJR0tR_zwRuRKLuIxCsaVVe9zJ-HYQ2_s2jMSm4Vbx7iyUBPzT33DjKWuyBe8dR4BWZwv7UejQeB1ttZLWcJ8

#Này là gửi mail xác nhận

EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'#PHƯƠNG THỨC GỬI MAIL

EMAIL_HOST='smtp.gmail.com' #MÁY CHỦ

EMAIL_PORT=587

EMAIL_USE_TLS=True #MÃ HÓA BẢO VỆ THÔNG TIN

EMAIL_HOST_USER=env('EMAIL_HOST_USER')

EMAIL_HOST_PASSWORD=env('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL='App Donate Support <trannghi1672004@gmail.com>' # EMAIL SẼ THẤY GỬI TỪ FROM:

#NÀY LÀ NGƯỜI DÙNG DÙNG MAIL XÁC THƯC allauth

ACCOUNT_LOGIN_METHODS = ['email'] #Dùng email đăng nhập

ACCOUNT_SIGNUP_FIELDS = ['email*']#các trường bắt buộc để tạo account

ACCOUNT_EMAIL_VERIFICATION='mandatory' #để confirm email, và bắt buộc phải confirm để đăng nhập

ACCOUNT_UNIQUE_EMAIL=True #mỗi email chỉ 1 tài khoản duy nhất

ACCOUNT_CONFIRM_EMAIL_ON_GET=False  # nếu True là cần nhân nút truyền token về ngay, False thì chỉ cần nhấn link để gửi token về

ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1 #Thời hạn hết hạn verify email

ACCOUNT_RATE_LIMITS={'confirm_email':'5/m'} # Thời gian cool down sau mỗi lần resend link

ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION=True #đăng nhập luôn sau khi confirm email

ACCOUNT_PASSWORD_MIN_LENGTH = 8 #độ dài tối thiểu mk là 8

SOCIALACCOUNT_AUTO_SIGNUP = True # true là login gg mà chưa có tk thì tạo luôn tk, false thì cần 1 bước điền email,username...

SOCIALACCOUNT_ADAPTER = "custome_authen.adapter.MySocialAccountAdapter"

AUTHENTICATION_BACKENDS=[

    'axes.backends.AxesStandaloneBackend',#axes

    'rules.permissions.ObjectPermissionBackend', #rules check quyền

    'django.contrib.auth.backends.ModelBackend',

    'allauth.account.auth_backends.AuthenticationBackend',#allauth

]
# đăng kí với gg và fb để đăng nhập đc

SOCIALACCOUNT_PROVIDERS = {

    'google': {

        'APP': {

            'client_id': env.list('GOOGLE_CLIENT_ID'),

            'secret': env.list('GOOGLE_SECRET'),

            'key': ''

        },

        'SCOPE': ['profile', 'email'],

        'AUTH_PARAMS': {

            'access_type': 'offline',

            'prompt': 'consent'  # Bắt buộc Google luôn hỏi quyền

        }

    },

    # 'facebook':{

    #     'APP':{

    #         'client_id':'',

    #         'secret':'',

    #         'key':''

    #     }

    # }

}

# Axes, ipware

AXES_ENABLED = True  # dùng chống bruteforce login

AXES_FAILURE_LIMIT = 7  # giới hạn lần sai

AXES_CACHE_TIMEOUT = 60 * 60  # reset lại sau từ n lần sai thành 0 nếu sau 1h

AXES_COOLOFF_TIME = timedelta(hours=1)  # Số giờ cooldown sau n lần sai

AXES_LOCK_OUT_AT_FAILURE = True  # Khoá tài khoản sau khi vượt quá số lần đăng nhập sai

AXES_RESET_ON_SUCCESS = True  # reset khi đăng nhập thành công

AXES_USERNAME_FORM_FIELD = 'email'  # k dùng username login thì chỉ định email thay thế

AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address']  # lockout theo username và ip

AXES_ENABLE_ACCESS_FAILURE_LOG = True  # log lại các lần đăng nhập thất bại

USE_X_FORWARDED_HOST = True  # nếu dùng proxy ngược như nginx

X_FRAME_OPTIONS = 'SAMEORIGIN'  # Ngăn chặn clickjacking tức là trang web bị load trong iframe của trang khác, chỉ cho root domain load <iframe>

REFERRER_POLICY = 'strict-origin-when-cross-origin'  # User ở https://yoursite.com/profile/123 click link sang google.com chỉ còn https://yoursite.com để bảo vệ thông tin

IPWARE_USE_X_FORWARDED_FOR = True

IPWARE_IP_HEADER = 'HTTP_X_FORWARDED_FOR'

IPWARE_META_PRECEDENCE_ORDER = [  # Thứ tự ưu tiên header để tìm IP (tùy môi trường)

    'HTTP_CF_CONNECTING_IP',

    'HTTP_X_FORWARDED_FOR',

    'HTTP_X_REAL_IP',

    'REMOTE_ADDR',

]

IPWARE_PRIVATE_IP_PREFIX = ('10.', '192.168.', '172.', '127.',
                            'fc00:')  # Dải IP nội bộ (private IP range) để không ghi lại

IPWARE_TRUSTED_PROXY_LIST = ['203.0.113.5', '198.51.100.0/24']  # Danh sách proxy đáng tin cậy

AXES_IPWARE_PROXY_COUNT = 1  # số proxy giữa client và server

AXES_IPWARE_META_PRECEDENCE_ORDER = IPWARE_META_PRECEDENCE_ORDER

# CORS

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')  # danh sách các domain đc phép truy cập api

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')  # danh sách các domain đc phép gửi csrf token

CORS_ALLOW_CREDENTIALS = True  # bắt buộc để gửi cookie

from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = list(default_headers) + ['content-type', 'authorization',
                                              'X-CSRFToken']  # thêm csrf token và bearer vào cho phép truy cập

if not DEBUG:  # chỉ chạy nếu debug là false tức chạy product

    SECURE_CONTENT_TYPE_NOSNIFF = True  # không cho đoán định dạng file

    SECURE_BROWSER_XSS_FILTER = True  # bộ lọc tránh xss truyền sscript

    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    SECURE_HSTS_SECONDS = 31536000  # nếu dùng HTTPS, nếu ng dùng dùng http vẫn redirect về http trong 1 năm tới

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # áp dụng cho tất cả domain kể cả sub domain

    SECURE_HSTS_PRELOAD = True

    SECURE_SSL_REDIRECT = True  # chuyển hướng http-> https(sau này deploy bật), http khác https và https có mã hóa

    # mới

    SESSION_COOKIE_SECURE = True  # chỉ cho gửi cookie nếu là https

    CSRF_COOKIE_SECURE = True  # csrf cho https

    SESSION_COOKIE_HTTPONLY = True  # Đảm bảo JS không đọc được Session Cookie

    SESSION_COOKIE_SAMESITE = 'Lax'  # cho phép gửi cookie trong 1 số liên trang và cấm phương thức post

    CSRF_COOKIE_SAMESITE = 'Lax'

# CSP tránh clickjacking và các tấn công XSS

from csp.constants import SELF, NONE

CONTENT_SECURITY_POLICY = {

    "EXCLUDE_URL_PREFIXES": ["/supremacy/admin", '/api/docs/'],
    # Loại trừ trang admin và docs khỏi CSP để tránh lỗi hiển thị

    "REPORT_ONLY": False,  # Chế độ chỉ báo cáo, không chặn

    "DIRECTIVES": {

        "default-src": [SELF],  # Mặc định chỉ cho phép tải tài nguyên từ chính server

        "script-src": [SELF, "accounts.google.com", "apis.google.com"],
        # ✅ Cho phép script nội bộ (cần nếu Swagger UI hoặc Django template)

        "style-src": [SELF, "accounts.google.com", "apis.google.com"],  # ✅ Cho phép CSS nội bộ

        "img-src": [SELF, "data:", "res.cloudinary.com"],  # ✅ Cho phép ảnh nội bộ và ảnh base64

        "connect-src": [SELF, f"wss://{env('DOMAIN', default='socialnetwork.dpdns.org')}",
                        f"wss://api.{env('DOMAIN', default='socialnetwork.dpdns.org')}", "accounts.google.com",
                        "oauth2.googleapis.com", 'https://api.socialnetwork.dpdns.org', "apis.google.com", ],
        # Cho phép fetch/xhr từ chính server

        "form-action": [SELF],  # ✅ Không cho gửi form ra ngoài

        "frame-ancestors": [SELF],
        # ✅ Ngăn clickjacking web khác nhứng web mình vào, ví dụ khi web khác nhúng web mình vào, nó gọi api tới web mình và phát hiện header 'self', k cho nhúng

        "base-uri": [SELF],  # ✅ Giới hạn `<base>` tag

        "object-src": [NONE],  # ✅ Ngăn Flash, PDF embeds

        "font-src": [SELF, "fonts.gstatic.com"],  # Cho phép nhúng font nếu dùng Google Font hoặc font local

        "media-src": [SELF, "res.cloudinary.com"],
        # Cho phép nhúng audio/video bạn host, nếu video/ảnh hosted trên server

        "frame-src": ["https://www.youtube.com", "https://player.vimeo.com", "accounts.google.com"]
        # kiểm soát web mình đc nhúng gì

    }

}
#=======================================SILK=============================================================================
SILKY_PYTHON_PROFILER = False            # Bật profiling cho Python code
SILKY_PYTHON_PROFILER_BINARY = True     # Lưu profile ở dạng binary (có thể dùng với tools như SnakeViz)
SILKY_MAX_REQUEST_BODY_SIZE = -1        # Lưu toàn bộ body request (mặc định là 100kb)
SILKY_MAX_RESPONSE_BODY_SIZE = -1       # Lưu toàn bộ body response
SILKY_INTERCEPT_PERCENT = 100           # % request được Silk ghi nhận
# =====================================================================================================================================================================================
# cacheops
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"
REDIS_HOST = env("REDIS_HOST", default="127.0.0.1")

CACHEOPS_REDIS = {
    'host': REDIS_HOST,
    'port': 6379,
    'db': 1,  # db 1
    'password' : env('REDIS_PASSWORD', default=''),
    'socket_timeout': 3,
}
CACHEOPS_DEFAULTS = {
    'timeout': 60*15,
    'local_get': False, # TẮT MẶC ĐỊNH: Bắt buộc gọi Redis để lấy data mới nhất,local get là dùng ram lưu .get() nhưng lưu vào process k qua redis dễ bị k chính xác khi yêu càu realtime
}
CACHEOPS = {
    # ở tất cả bảng, cache(lưu vào bộ nhớ phụ và reuse) ví dụ get,filter,count...trong 15p.
    #ví dụ ng dùng gọi api lần 1 nó lưu vào cache, nó phát hiện có bài đăng mới nó sẽ tự gọi lại và lưu cache mà k cần đợi timeout
}
# ==========================================================================================================================================================================================================
# Channels
ASGI_APPLICATION = "backend.asgi.application"  # setting để runserver có thể chạy asgi
# redis chạy channels
# dùng daphne để chạy cả http + websocket

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [f"redis://:{env('REDIS_PASSWORD', default='')}@{REDIS_HOST}:6379/0"],  # db 0
            "capacity": 1500,  # Giới hạn hàng đợi tin nhắn
            "expiry": 30,     # Tin nhắn chờ trong 30s nếu ko ai nhận thì hủy
            "symmetric_encryption_keys": [env('SECRET_KEY')], # bảo mật dữ liệu
        },
    },
}
# ============================================================================================
# lưu query vào cache  tránh gọi trong db
CACHES = {  # xài redis, set cache default là redis db 2
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://:{env('REDIS_PASSWORD', default='')}@{REDIS_HOST}:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True, #  Redis sập web vẫn sống
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100, #giữ kết nối redis
                "retry_on_timeout": True,#và tự kết nối lại
                "health_check_interval": 30,  #  Kiểm tra sức khỏe kết nối
                "socket_connect_timeout": 5,  # Không bắt User đợi lâu khi treo
                "socket_keepalive": True,     # Giữ kết nối luôn sẵn sàng
            },
            "PICKLE_VERSION": -1, #chọn bảng cao nhất hỗ trợ để nhanh hơn dùng nén dữ liệu lưu vào redis
        },
        "TIMEOUT": 300, # xóa dữ liệu sau 5p
        }
    }
#===============================================================================================
#Elastic search
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': env('ELASTICSEARCH_URL', default='http://elasticsearch:9200')
    }
}
#======================CELERY============================================
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://redis:6379/3') # Redis làm nơi chứa task chờ xử lý
CELERY_RESULT_BACKEND = 'django-db' #lưu kết quả task vào Django DB

# định dạng data khi truyền task
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'

# production — giới hạn task
CELERY_TASK_TIME_LIMIT = 300        # task chạy tối đa 5 phút, quá 5p thì kill
CELERY_TASK_SOFT_TIME_LIMIT = 240   # cảnh báo trước 1 phút trước khi kill task để cleanup
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # restart worker sau 1000 task tránh memory leak
CELERY_TASK_ACKS_LATE = True        # chỉ xác nhận task sau khi chạy xong,nếu chưa xong mà lỗi thì retry, tránh mất task khi worker crash
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # mỗi worker chỉ lấy 1 task, tránh 1 worker ôm hết

# queue riêng cho từng loại task
CELERY_TASK_ROUTES = {
    'api.tasks.push_notification_task': {'queue': 'notifications'},
    'api.tasks.send_email_task': {'queue': 'emails'},
}





