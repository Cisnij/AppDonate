# documents.py
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, token_filter
from user.models import Page

#=================================FILTER để lọc ra từ từ tìm kiếm=================================
# Bộ lọc chuyển tiếng Việt có dấu -> không dấu, preserver để lưu cả bản k dấu và có dấu
ascii_fold = token_filter("ascii_fold", type="asciifolding", preserve_original=True)
#cắt nhỏ từ để tìm kiếm từng phần kiểm tra ví dụ c->co->con , bắt đầu từ cắt từ kí tự thứ 2 và cắt max 20
ngram_filter = token_filter("ngram_filter", type="edge_ngram", min_gram=2, max_gram=20)
shingle_filter = token_filter(
    "shingle_filter",
    type="shingle",
    min_shingle_size=2,
    max_shingle_size=3,           # tạo cụm 2-3 từ: "trần nghị", "trần nghị nguyễn"
    output_unigrams=True          # vẫn giữ từ đơn
)
synonym_filter = token_filter(
    "synonym_filter",
    type="synonym",
    synonyms=[
        # thêm từ đồng nghĩa domain của bạn
    ]
)
#=============================ÁP DỤNG FILTER VÀO TÌM KIẾM===============================================
vn_index_analyzer  = analyzer( # chuyển thành chuỗi thường và băt đầu phân tích băm nhỏ( dùng cho lưu)
    "vn_index_analyzer",
    tokenizer="standard", #chia câu thành từ đơn lẻ ví dụ con cò-> con và cò và lưu dạng token
    filter=["lowercase", ascii_fold, synonym_filter, shingle_filter, ngram_filter] # chuyển thành chữ thường và lọc
)

vn_search_analyzer = analyzer(#tìm kiếm không băm ngram, chỉ lowercase + bỏ dấu ( dùng cho tìm kiếm)
    "vn_search_analyzer",
    tokenizer="standard",
    filter=["lowercase", ascii_fold,synonym_filter,]  # không có ngram_filter
)
'''flow là người dùng nhập key sẽ dùng vn_analyzer băm nhỏ thành đơn lẻ và lưu, cũng lưu luôn từ có dấu
và từ bỏ dấu, sau đó mới trả kết quả có sẵn nếu trùng với thằng băm. Sau này có tìm từ mới thì trùng với
thằng đã bị băm thì chỉ cần trả ra'''

@registry.register_document
class PageDocument(Document):
    page_name = fields.TextField(analyzer=vn_index_analyzer, search_analyzer=vn_search_analyzer)
    class Index:
        name = "page"
        settings = {'number_of_shards': 3, 'number_of_replicas': 1,'max_ngram_diff': 18,}#shards để chia nhỏ dữ liệu trong db để tìm, replicas bản sao dự phòng
    class Django:
        model = Page
        fields = []
        signals ='auto'  # đăng kí signal để khi có update hoặc create sẽ tự phân tách là lưu token trong db elastic cho search
    def get_queryset(self):
        return super().get_queryset().filter(deleted__isnull=True)

# # 1. Xóa index cũ (nếu có)
# python manage.py search_index --delete
#
# # 2. Tạo lại index mới theo document đã khai báo
# python manage.py search_index --create

# python manage.py search_index --rebuild

# # 3. Đẩy toàn bộ data từ DB vào ES
# python manage.py search_index --populate