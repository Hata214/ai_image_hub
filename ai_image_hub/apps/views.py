from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from deep_translator import GoogleTranslator
from .models import AIImage
from .services import generate_ai_image, check_api_health

@login_required
def generate_image_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Xử lý nút Kiểm tra sức khỏe API
        if action == 'check_api':
            is_ok, msg = check_api_health()
            if is_ok:
                messages.success(request, f"✅ {msg}")
            else:
                messages.error(request, f"❌ {msg}")
            return redirect('generate')

        # Xử lý xóa ảnh
        if action == 'delete_image':
            image_id = request.POST.get('image_id')
            try:
                img = AIImage.objects.get(id=image_id, user=request.user)
                img.delete()
                messages.success(request, "Đã xóa ảnh thành công.")
            except AIImage.DoesNotExist:
                messages.error(request, "Không tìm thấy ảnh để xóa.")
            return redirect('generate')

        # Xử lý nút Tạo ảnh
        prompt = request.POST.get('prompt')
        
        if not prompt:
            messages.error(request, "Vui lòng nhập mô tả!")
            return redirect('generate')

        # Dịch prompt sang Tiếng Anh để AI hiểu rõ hơn
        try:
            translated_prompt = GoogleTranslator(source='auto', target='en').translate(prompt)
        except Exception as e:
            print(f"Lỗi dịch thuật: {e}")
            translated_prompt = prompt

        # 1. Tạo bản ghi tạm trong DB
        image_obj = AIImage.objects.create(
            user=request.user,
            prompt=prompt,
            refined_prompt=translated_prompt,
            status='pending'
        )

        # 2. Gọi API Hugging Face với chuỗi tiếng Anh đã dịch
        image_file = generate_ai_image(translated_prompt)

        if image_file:
            # 3. Lưu ảnh vào DB
            image_obj.image.save(f"ai_{image_obj.id}.png", image_file)
            image_obj.status = 'completed'
            image_obj.save()
            messages.success(request, "Đã tạo ảnh thành công!")
        else:
            image_obj.status = 'failed'
            image_obj.save()
            messages.error(request, "Lỗi hệ thống, vui lòng thử lại sau.")

        return redirect('generate')

    # Lấy danh sách ảnh của user để hiển thị
    my_images = AIImage.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'generator/index.html', {
        'images': my_images
    })
