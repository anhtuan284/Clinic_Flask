from flask import redirect, request
from flask_admin import BaseView, Admin
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, current_user

from clinicapp import app, db, utils
from clinicapp.dao import get_medicines, get_categories, get_category_medicines, add_or_update_medicine, \
    delete_all_category_medicine_by_medicine_id, add_category_medicine, get_medicine_by_id, delete_medicine_by_id, \
    get_categories_by_medicine_id
from clinicapp.models import UserRole, User, Doctor, Nurse, Patient, Policy, Medicine, Unit, Category, MedicineUnit


class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN


class AuthenticatedBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN


class MyUserView(AuthenticatedView):
    column_list = ['id', 'name', 'phone', 'username', 'email', 'address', 'role']
    column_searchable_list = ['username', 'name', 'phone']
    column_editable_list = ['name', ]
    can_export = True
    column_filters = ['role']
    column_labels = {
        'id': 'ID',
        'name': 'Họ Tên',
        'phone': 'SĐT',
        'username': 'Tên người dùng',
        'email': 'Email',
        'address': 'Địa chỉ',
        'role': 'Vai trò',
    }

    def on_model_change(self, form, model, is_created):
        # Kiểm tra xem mật khẩu đã được thay đổi hay không
        if 'password' in form:
            password = form.password.data
            if password:
                # Băm mật khẩu mới và lưu vào model
                hashed_password = utils.hash_password(password)
                model.password = hashed_password
        super().on_model_change(form, model, is_created)

    def on_form_prefill(self, form, id):
        # Thực hiện cùng một băm mật khẩu khi hiển thị form để chỉnh sửa
        form.password.data = ''


class DoctorAdminView(AuthenticatedView):
    column_list = ['id']
    column_labels = {
        'id': 'User ID'
    }


class NurseAdminView(AuthenticatedView):
    column_list = ['id']
    column_labels = {
        'id': 'User ID'
    }


class PatientAdminView(AuthenticatedView):
    column_list = ['id']
    column_labels = {
        'id': 'User ID'
    }


class PolicyAdminView(AuthenticatedView):
    column_list = ['name', 'value', 'admin']
    column_searchable_list = ['name', 'value']
    column_editable_list = ['name', 'value']
    column_labels = {
        'name': 'Tên Quy Định',
        'value': 'Giá Trị'
    }


class MedicineAdminView(AuthenticatedView):
    column_list = ['name', 'gia', 'usage', 'exp']
    column_searchable_list = ['name']
    column_editable_list = ['name', 'price', 'usage', 'exp']


class CategoryAdminView(AuthenticatedView):
    column_list = ['name', 'medicine']


# class MedicineCategoryAdminView(ModelView):
#     column_list = ['category', 'medicine']
#     column_labels = {'category': 'Danh Mục', 'medicine': 'Thuốc'}
#     column_searchable_list = ['category.name', 'medicine.name']
#     column_filters = ['category', 'medicine']
#     form_ajax_refs = {'medicine': {'fields': ['name']}}


class UnitAdminView(AuthenticatedView):
    column_list = ['id', 'name']


class StatsView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        return self.render('admin/stats.html')


class LogoutView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')


class ThuocView(AuthenticatedBaseView):
    @expose('/')
    def index(self):
        gia_bat_dau = request.args.get('gia_bat_dau')
        gia_ket_thuc = request.args.get('gia_ket_thuc')
        han_dung_bat_dau = request.args.get('han_dung_bat_dau')
        han_dung_ket_thuc = request.args.get('han_dung_ket_thuc')
        name = request.args.get('name')
        danhmuc_id = request.args.get('danhmuc_id')

        return self.render(
            'admin/thuoc.html',
            thuocs=get_medicines(
                price_bat_dau=gia_bat_dau,
                price_ket_thuc=gia_ket_thuc,
                han_dung_bat_dau=han_dung_bat_dau,
                han_dung_ket_thuc=han_dung_ket_thuc,
                name=name,
                category_id=danhmuc_id
            ),
            danhmucs=get_categories(),
            danhmucthuocs=get_category_medicines()
        )

    @expose('/thuocs/', methods=['get', 'post'])
    def add_thuoc(self):
        if request.method.__eq__('POST'):
            id = request.form.get('id')
            gia = request.form.get('gia')
            name = request.form.get('name')
            cach_dung = request.form.get('cach_dung')
            han_su_dung = request.form.get('han_su_dung')
            ds_danh_muc = request.form.getlist('ds_danh_muc')

            thuocMoiId = add_or_update_medicine(
                id=id,
                price=gia,
                name=name,
                usage=cach_dung,
                exp=han_su_dung
            )

            delete_all_category_medicine_by_medicine_id(thuocMoiId)
            for dm in ds_danh_muc:
                add_category_medicine(category_id=int(dm), medicine_id=thuocMoiId)

        return self.render('admin/them_thuoc.html', cates=get_categories())

    @expose('/thuocs/<id>', methods=['get', 'post'])
    def update_thuoc(self, id):
        thuoc = get_medicine_by_id(id)

        if request.method.__eq__('POST'):
            delete_medicine_by_id(id)
            return redirect('/admin/thuocview/')
        else:
            return self.render(
                'admin/them_thuoc.html',
                cates=get_categories(),
                thuoc=thuoc,
                currentcates=get_categories_by_medicine_id(id)
            )


class MyDanhMucView(AuthenticatedView):
    @expose('/')
    def index(self):
        return self.render('admin/danh_muc.html', danhmucs=get_categories())


class MyCategoryView(AuthenticatedView):
    column_list = ['id', 'name']

    form_widget_args = {
        'medicine_category': {
            'disabled': True
        }
    }


class MyMedicineUnitView(AuthenticatedView):
    column_list = ['id', 'unit', 'medicine', 'quantity', 'medicine_details']

    column_labels = {
        'medicine_details': 'Phiếu khám tương ứng',
    }

    form_widget_args = {
        'medicine_details': {
            'disabled': True
        }
    }


admin = Admin(app, name='Clinic Website', template_mode='bootstrap4')

admin.add_view(ThuocView(name="Thuốc"))
admin.add_view(UnitAdminView(Unit, db.session, name="Đơn vị"))
admin.add_view(MyMedicineUnitView(MedicineUnit, db.session, name="Thuốc-Đơn vị"))
admin.add_view(MyCategoryView(Category, db.session, name='Danh mục'))
admin.add_view(MyUserView(User, db.session))
admin.add_view(PolicyAdminView(Policy, db.session, name="Quy Định"))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(LogoutView(name='Đăng xuất'))
