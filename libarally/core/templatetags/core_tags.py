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
