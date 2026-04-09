from django.db import models
from django.contrib.auth.models import User

class AIImage(models.Model):
    # Liên kết với người dùng
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="images")
    
    # Dữ liệu về Prompt
    prompt = models.TextField(help_text="Mô tả của người dùng")
    refined_prompt = models.TextField(blank=True, null=True, help_text="Mô tả đã được AI tối ưu")
    
    # Dữ liệu về File ảnh
    image = models.ImageField(upload_to="ai_generated/%Y/%m/%d/", blank=True)
    
    # Thông số kỹ thuật
    model_name = models.CharField(max_length=100, default="dall-e-3")
    resolution = models.CharField(max_length=20, default="1024x1024")
    
    # Trạng thái xử lý
    status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')],
        default='pending'
    )
    
    # --- ĐÂY LÀ PHẦN BÀI TẬP CỦA BẠN ---
    is_public = models.BooleanField(default=False, help_text="Công khai ảnh này với mọi người")
    # -----------------------------------

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.prompt[:30]}"