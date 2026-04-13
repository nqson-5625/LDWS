from fastapi import HTTPException, status

# Hàm OUTER (Factory) tạo ra các hàm kiểm tra
def require_roles(*allowed_roles): # * thể hiện hàm nhận bao nhiêu tham số cũng được
    # Hàm INNER (hàm thực sự chạy)
    def checker(current_user):
        # Kiểm tra role của current user có nằm trong các allowed_roles không
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        
        return current_user
    
    return checker # Trả về tên hàm INNER - phục vụ Depend()