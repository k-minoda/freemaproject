from django.shortcuts import render

# Create your views here.
from django.views.generic import CreateView
from django.urls import reverse_lazy
# from requests import post
from .forms import PhotoPostForm
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from .models import PhotoPost
from django.views.generic import TemplateView, ListView, DetailView, DeleteView
from django.db.models import Q # get_queryset()用に追加
from django.contrib import messages #　検索結果のメッセージのため追加


class IndexView(TemplateView):
    template_name = 'index.html'


class PostSuccessView(TemplateView):
    template_name = 'post_success.html'

# デコレーターにより、CreatePhotoViewへのアクセスはログインユーザーに限定される
# ログイン状態でなければsettings.pyのLOGIN_URLにリダイレクトされる


@method_decorator(login_required, name='dispatch')
class CreatePhotoView(CreateView):
    form_class = PhotoPostForm
    template_name = "post_photo.html"

    # データベースへの登録完了後のリダイレクト先
    success_url = reverse_lazy('freema:post_done')

    def form_valid(self, form):
        # commit=FalseにしてPOSTされたデータを取得
        postdata = form.save(commit=False)
        # 投稿ユーザーのidを取得してモデルのuserフィールドに格納
        postdata.user = self.request.user
        # 投稿データをデータベースに登録
        postdata.save()
        return super().form_valid(form)


class IndexView(ListView):
    template_name = 'index.html'

    # モデルPhotoPostのオブジェクトにorder_by()を適用して
    # 投稿日時の降順で並べ替える
    queryset = PhotoPost.objects.order_by('-posted_at')
    # 1ページに表示するレコードの件数
    paginate_by = 9


class CategoryView(ListView):
    template_name = "index.html"
    paginate_by = 9

    def get_queryset(self):
        # self.kwargsでキーワードの辞書を取得し、
        # categoryキーの値(Categorysテーブルのid)を取得
        category_id = self.kwargs["category"]
        # filter(フィールド名=id)で絞り込む
        categories = PhotoPost.objects.filter(category=category_id).order_by(
            "-posted_at"
        )
        return categories


class UserView(ListView):
    template_name = "index.html"
    paginate_by = 9

    def get_queryset(self):
        # self.kwargsでキーワードの辞書を取得し、
        # userキーの値(ユーザーテーブルのid)を取得
        user_id = self.kwargs["user"]
        # filter(フィールド名=id)で絞り込む
        user_list = PhotoPost.objects.filter(
            user=user_id).order_by("-posted_at")
        return user_list


class DetailView(DetailView):
    template_name = 'detail.html'
    model = PhotoPost


class MypageView(ListView):
    template_name = "mypage.html"

    # 1ページに表示するレコードの件数
    paginate_by = 9

    def get_queryset(self):
        # 現在ログインしているユーザー名はHttpRequest.userに格納されている
        # filter(userフィールド=userオブジェクト)で絞り込む
        queryset = PhotoPost.objects.filter(user=self.request.user).order_by(
            "-posted_at"
        )

        return queryset


class PhotoDeleteView(DeleteView):
    template_name = 'photo_delete.html'
    model = PhotoPost

    # 処理完了後にマイページにリダイレクト
    success_url = reverse_lazy('freema:mypage')

    def delete(self, request, *args, **kwargs):
        # スーパークラスのdelete()を実行
        return super().delete(request, *args, **kwargs)



    


class IndexList(ListView):
    template_name = 'get_queryset.html'
    paginate_by = 2
    # context_object_name = 'post_list'

    def get_queryset(self): # 検索機能のために追加
        queryset = PhotoPost.objects.order_by('-comment')
        query = self.request.GET.get('query')

        if query:
            queryset = queryset.filter(
            Q(title__icontains=query) | Q(comment__icontains=query)
            )
        messages.add_message(self.request, messages.INFO, query) #　検索結果メッセージ
        return queryset
