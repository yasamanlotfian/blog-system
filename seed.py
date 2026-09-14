from database import SessionLocal, engine, Base

from passlib.context import CryptContext

from tables.user import User
from tables.Permission import Permission
from tables.user_permissions import UserPermission

from tables.blog import Blog
from tables.category import Category
from tables.gallery import Gallery
from tables.comment import Comment
from tables.tag import Tag
from tables.blog_tag import blog_tags
from tables.file import File as FileTable
from  tables.video import Video


Base.metadata.create_all(bind=engine)


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def seed_data():

    print("DATA GENERATION STARTED")

    db = SessionLocal()

    try:

        if db.query(User).first():
            print("Already seeded!")
            return


  
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password=pwd_context.hash("12345893"),
            role="admin"
        )

        operator_user = User(
            username="operator",
            email="operator@example.com",
            password=pwd_context.hash("12345679"),
            role="operator"
        )

        normal_user = User(
            username="user",
            email="user@example.com",
            password=pwd_context.hash("23453682"),
            role="user"
        )

        db.add_all([
            admin_user,
            operator_user,
            normal_user
        ])

        db.flush()



        create_blog_permission = Permission(name="blog_create")
        read_blog_permission = Permission(name="blog_read")
        update_blog_permission = Permission(name="blog_update")
        delete_blog_permission = Permission(name="blog_delete")

        create_gallery_permission = Permission(name="gallery_create")
        read_gallery_permission = Permission(name="gallery_read")
        update_gallery_permission = Permission(name="gallery_update")
        delete_gallery_permission = Permission(name="gallery_delete")

        create_tag_permission = Permission(name="tag_create")
        read_tag_permission = Permission(name="tag_read")
        update_tag_permission = Permission(name="tag_update")
        delete_tag_permission = Permission(name="tag_delete")

        create_comment_permission = Permission(name="comment_create")
        read_comment_permission = Permission(name="comment_read")
        delete_comment_permission = Permission(name="comment_delete")

        create_user_permission = Permission(name="user_create")
        read_user_permission = Permission(name="user_read")
        update_user_permission = Permission(name="user_update")
        delete_user_permission = Permission(name="user_delete")


        db.add_all([

            create_blog_permission,
            read_blog_permission,
            update_blog_permission,
            delete_blog_permission,

            create_gallery_permission,
            read_gallery_permission,
            update_gallery_permission,
            delete_gallery_permission,

            create_tag_permission,
            read_tag_permission,
            update_tag_permission,
            delete_tag_permission,

            create_comment_permission,
            read_comment_permission,
            delete_comment_permission,

            create_user_permission,
            read_user_permission,
            update_user_permission,
            delete_user_permission,
        ])

        db.flush()



        admin_permissions = [

            create_blog_permission,
            read_blog_permission,
            update_blog_permission,
            delete_blog_permission,

            create_gallery_permission,
            read_gallery_permission,
            update_gallery_permission,
            delete_gallery_permission,

            create_tag_permission,
            read_tag_permission,
            update_tag_permission,
            delete_tag_permission,

            create_comment_permission,
            read_comment_permission,
            delete_comment_permission,

            create_user_permission,
            read_user_permission,
            update_user_permission,
            delete_user_permission,
        ]


        for permission in admin_permissions:

            db.add(
                UserPermission(
                    user_id=admin_user.id,
                    permission_id=permission.id,
                    granted_by=admin_user.id
                )
            )


        operator_permissions = [

            create_blog_permission,
            read_blog_permission,
            update_blog_permission,

            update_gallery_permission,

            create_tag_permission,
            read_tag_permission,
            update_tag_permission,

            read_comment_permission,
            delete_comment_permission,

            delete_user_permission,
        ]


        for permission in operator_permissions:

            db.add(
                UserPermission(
                    user_id=operator_user.id,
                    permission_id=permission.id,
                    granted_by=admin_user.id
                )
            )



        normal_user_permissions = [

            read_blog_permission,
            read_tag_permission,
            read_comment_permission,
        ]


        for permission in normal_user_permissions:

            db.add(
                UserPermission(
                    user_id=normal_user.id,
                    permission_id=permission.id,
                    granted_by=admin_user.id
                )
            )


        db.flush()



        category1 = Category(name="مو")
        category2 = Category(name="ناخن")
        category3 = Category(name="پوست")
        category4 = Category(name="میکاپ")

        db.add_all([
            category1,
            category2,
            category3,
            category4
        ])

        db.flush()


        tag1 = Tag(name="مراقبت از مو")
        tag2 = Tag(name="مانیکور")
        tag3 = Tag(name="پاکسازی پوست")
        tag4 = Tag(name="آرایش صورت")
        tag5 = Tag(name="موهای خشک")

        db.add_all([
            tag1,
            tag2,
            tag3,
            tag4,
            tag5
        ])

        db.flush()



        blog1 = Blog(
            title="نکات مهم برای مراقبت از مو",
            slug="hair-care-tips",
            seo_title="بهترین روش مراقبت از مو",
            description="چند نکته ساده برای داشتن موهایی سالم و زیبا.",
            content="""
مراقبت از مو یکی از مهم‌ترین کارها برای داشتن موهایی سالم و زیبا است.

برای مراقبت از مو باید به شست‌وشوی صحیح، انتخاب شامپوی مناسب،
استفاده از نرم‌کننده و ماسک مو توجه کرد. انتخاب محصولات مناسب
برای موهای خشک، موهای چرب و موهای معمولی می‌تواند به سلامت و
زیبایی مو کمک کند.

همچنین بهتر است استفاده از سشوار و اتو مو را کاهش دهید و از حرارت
زیاد برای موها استفاده نکنید. تغذیه مناسب، نوشیدن آب کافی و
مراقبت از پوست سر نیز در سلامت موها تأثیر زیادی دارد.
""",
            category_id=category1.id,
            view_num=0
        )


        blog2 = Blog(
            title="چگونه از ناخن‌های خود مراقبت کنیم؟",
            slug="nail-care-tips",
            seo_title="روش‌های مراقبت از ناخن",
            description="نکات ساده برای داشتن ناخن‌های سالم و زیبا.",
            content="""
مراقبت از ناخن‌ها برای داشتن دست‌هایی زیبا و سالم اهمیت زیادی دارد.

تمیز نگه داشتن ناخن‌ها، کوتاه کردن منظم آن‌ها و استفاده از محصولات
مراقبتی مناسب می‌تواند به سلامت ناخن کمک کند.

برای جلوگیری از شکنندگی ناخن بهتر است از تماس طولانی مدت با مواد
شوینده جلوگیری کرد و هنگام انجام کارهای خانه از دستکش استفاده شود.

استفاده از روغن و کرم مرطوب‌کننده برای ناخن و پوست اطراف آن نیز
می‌تواند باعث حفظ رطوبت و جلوگیری از خشکی شود.

تغذیه مناسب نیز در رشد و تقویت ناخن‌ها نقش مهمی دارد.
""",
            category_id=category2.id,
            view_num=0
        )

        blog3 = Blog(
            title="مراقبت از پوست قبل از آرایش",
            slug="skin-care-before-makeup",
            seo_title="مراقبت از پوست قبل از میکاپ",
            description="چند نکته کاربردی برای آماده کردن پوست قبل از آرایش.",
            content="""
آماده کردن پوست قبل از آرایش یکی از مهم‌ترین مراحل برای داشتن
یک میکاپ زیبا و ماندگار است.

ابتدا باید پوست را به خوبی تمیز کرد تا آلودگی و چربی اضافی از
سطح پوست پاک شود.

پس از پاکسازی، استفاده از مرطوب‌کننده مناسب نوع پوست اهمیت زیادی
دارد. افرادی که پوست خشک دارند بهتر است از مرطوب‌کننده‌های مناسب
پوست خشک استفاده کنند و افرادی که پوست چرب دارند می‌توانند از
محصولات سبک‌تر استفاده کنند.

استفاده از ضدآفتاب در طول روز نیز اهمیت زیادی دارد.

آماده‌سازی صحیح پوست قبل از میکاپ باعث می‌شود آرایش بهتر روی پوست
قرار بگیرد و ظاهر طبیعی‌تری داشته باشد.
""",
            category_id=category3.id,
            view_num=0
        )


        blog4 = Blog(
            title="روش‌های مراقبت از موهای خشک",
            slug="dry-hair-care",
            seo_title="بهترین روش مراقبت از موهای خشک",
            description="روش‌های ساده برای مراقبت و تقویت موهای خشک.",
            content=""""
موهای خشک معمولاً به مراقبت و رطوبت بیشتری نیاز دارند.

استفاده از شامپوی مناسب موهای خشک و شست‌وشوی بیش از حد نکردن موها
می‌تواند به حفظ رطوبت مو کمک کند.

استفاده از نرم‌کننده و ماسک مو برای موهای خشک بسیار مفید است.

همچنین بهتر است استفاده از سشوار، اتو مو و سایر وسایل حرارتی
کاهش پیدا کند، زیرا حرارت زیاد می‌تواند خشکی و آسیب مو را بیشتر کند.

استفاده از محصولات مرطوب‌کننده و روغن‌های مناسب مو نیز می‌تواند
به نرم شدن و تقویت موها کمک کند.

تغذیه مناسب و نوشیدن آب کافی نیز برای سلامت مو اهمیت دارد.
""",
            category_id=category1.id,
            view_num=0
        )


        db.add_all([
            blog1,
            blog2,
            blog3,
            blog4
        ])

        db.flush()


        blog1.tags.extend([
            tag1
        ])

        blog2.tags.extend([
            tag2
        ])

        blog3.tags.extend([
            tag3,
            tag4
        ])

        blog4.tags.extend([
            tag1,
            tag5
        ])

        file1 = FileTable(
            original_file_url=(
                "https://images.unsplash.com/"
                "photo-1522337360788-8b13dee7a37e"
            ),
            optimized_file_url=(
                "https://images.unsplash.com/"
                "photo-1522337360788-8b13dee7a37e"
            ),
            crop_file_url=None,
            original_file_size=250000,
            optimized_file_size=120000,
            crop_file_size=None,
            mime_type="image/jpeg",
            file_type="image"
        )


        file2 = FileTable(
            original_file_url=(
                "https://images.unsplash.com/"
                "photo-1604654894610-df63bc536371"
            ),
            optimized_file_url=(
                "https://images.unsplash.com/"
                "photo-1604654894610-df63bc536371"
            ),
            crop_file_url=None,
            original_file_size=300000,
            optimized_file_size=150000,
            crop_file_size=None,
            mime_type="image/jpeg",
            file_type="image"
        )


        file3 = FileTable(
            original_file_url=(
                "https://images.unsplash.com/"
                "photo-1556228578-8c89e6adf883"
            ),
            optimized_file_url=(
                "https://images.unsplash.com/"
                "photo-1556228578-8c89e6adf883"
            ),
            crop_file_url=None,
            original_file_size=280000,
            optimized_file_size=140000,
            crop_file_size=None,
            mime_type="image/jpeg",
            file_type="image"
        )


        file4 = FileTable(
            original_file_url=(
                "https://images.unsplash.com/"
                "photo-1562322140-8baeececf3df"
            ),
            optimized_file_url=(
                "https://images.unsplash.com/"
                "photo-1562322140-8baeececf3df"
            ),
            crop_file_url=None,
            original_file_size=320000,
            optimized_file_size=160000,
            crop_file_size=None,
            mime_type="image/jpeg",
            file_type="image"
        )


        db.add_all([
            file1,
            file2,
            file3,
            file4,
        ])

        db.flush()


    

        gallery1 = Gallery(
            title="مراقبت از مو",
            file_id=file1.id,
            alt_text="مراقبت از مو"
        )


        gallery2 = Gallery(
            title="مراقبت از ناخن",
            file_id=file2.id,
            alt_text="مراقبت از ناخن"
        )


        gallery3 = Gallery(
            title="مراقبت از پوست",
            file_id=file3.id,
            alt_text="مراقبت از پوست"
        )


        gallery4 = Gallery(
            title="مراقبت از موهای خشک",
            file_id=file4.id,
            alt_text="مراقبت از موهای خشک"
        )


        db.add_all([
            gallery1,
            gallery2,
            gallery3,
            gallery4,
        ])



        comment1 = Comment(
            blog_id=blog1.id,
            name="سارا",
            content="مقاله خیلی مفیدی بود."
        )


        comment2 = Comment(
            blog_id=blog2.id,
            name="مریم",
            content="نکات مراقبت از ناخن خیلی خوب بود."
        )


        comment3 = Comment(
            blog_id=blog3.id,
            name="نگار",
            content="مطلب مفیدی درباره مراقبت از پوست بود."
        )


        comment4 = Comment(
            blog_id=blog4.id,
            name="زهرا",
            content="نکات مراقبت از موهای خشک خیلی مفید بود."
        )


        db.add_all([
            comment1,
            comment2,
            comment3,
            comment4
        ])



        db.commit()

        print("DATA GENERATION COMPLETED")


    except Exception as e:

        db.rollback()

        print("ERROR:", e)


    finally:

        db.close()


if __name__ == "__main__":
    seed_data()