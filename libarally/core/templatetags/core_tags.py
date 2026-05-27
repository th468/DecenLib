from django import template
from django.urls import reverse, NoReverseMatch
from books.models import Category

register = template.Library()

@register.inclusion_tag('common/includes/_category_sidebar.html')
def get_category_list():
    """
    全カテゴリを取得し、サイドバー用のテンプレートに渡す。
    """
    categories = Category.objects.all().order_by('name')
    return {'categories': categories}

@register.inclusion_tag('common/includes/_search_bar.html', takes_context=True)
def global_search_bar(context):
    """
    サイト全体で共通利用する検索バーを表示するタグ。
    現在の検索キーワードを初期値として保持する。
    """
    request = context.get('request')
    q = request.GET.get('q', '') if request else ""
    return {'q': q}

@register.simple_tag(takes_context=True)
def active_link(context, url_name, css_class='active'):
    """
    現在のURLが指定された url_name と一致する場合、css_class を返す。
    ナビゲーションのハイライトに使用。
    """
    request = context.get('request')
    if not request:
        return ""
    
    try:
        # url_name から実際のパスを逆引き
        target_url = reverse(url_name)
        # 現在のパスがターゲットURLで始まっているか判定
        # (前方一致にすることで、詳細画面等でも親メニューをハイライトできる)
        if request.path.startswith(target_url):
            return css_class
    except NoReverseMatch:
        pass
    
    return ""

@register.simple_tag
def relative_url(value, field_name, urlencode=None):
    """
    現在のURLパラメータを維持したまま、特定のパラメータを書き換える。
    """
    url = f'?{field_name}={value}'
    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        if encoded_querystring:
            url = f'{url}&{encoded_querystring}'
    return url


# --- 状態判定フィルタ ---

@register.filter
def is_lent_by(obj, user):
    """
    ユーザーが対象を現在借りているか判定。
    obj が Biblio の場合は「そのタイトルのいずれか」を、
    obj が Book の場合は「その個体」を借りているか判定。
    """
    if not user or not user.is_authenticated:
        return False
    from books.models import Biblio, Book
    from transactions.models import Lending

    if isinstance(obj, Biblio):
        return Lending.objects.ongoing().filter(book__biblio=obj, user=user).exists()
    elif isinstance(obj, Book):
        return Lending.objects.ongoing().filter(book=obj, user=user).exists()
    return False


@register.filter
def is_reserved_by(biblio, user):
    """ユーザーがその書誌を現在予約しているか判定"""
    if not user or not user.is_authenticated:
        return False
    from transactions.models import Reservation
    return Reservation.objects.ongoing().filter(biblio=biblio, user=user).exists()


@register.filter
def is_lent_by_others(biblio, user):
    """自分以外のユーザーがその書誌（のいずれかの在庫）を現在借りているか判定"""
    if not user or not user.is_authenticated:
        return False
    from transactions.models import Lending
    return Lending.objects.ongoing().filter(book__biblio=biblio).exclude(user=user).exists()


@register.filter
def user_lending(biblio, user):
    """ユーザーがその書誌を借りている場合、その Lending オブジェクトを返す"""
    if not user or not user.is_authenticated:
        return None
    from transactions.models import Lending
    return Lending.objects.ongoing().filter(book__biblio=biblio, user=user).first()
