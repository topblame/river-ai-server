# account/adapter/input/web/accounts_router.py

from fastapi import APIRouter, Depends, HTTPException, status

from account.adapter.input.web.session_helper import get_current_user
from account.application.usecase.account_usecase import AccountUseCase
from account.infrastructure.repository.account_repository_impl import (
    AccountRepositoryImpl,
)

router = APIRouter(
    tags=["accounts"],
)

# 간단 DI: 실제로는 Depends로 분리할 수도 있지만,
# 지금 구조에선 UseCase를 한 번 생성해서 재사용해도 무방.
account_usecase = AccountUseCase(AccountRepositoryImpl())


@router.get("/me")
async def get_me(user_id: int = Depends(get_current_user)):
    """
    세션에 담긴 user_id를 기준으로 현재 로그인한 계정 정보를 반환합니다.
    - 세션 쿠키(session_id)는 get_current_user()에서 처리.
    - 계정이 없으면 404 반환.
    """
    account = account_usecase.get_account_by_id(user_id)

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    return {
        "id": account.id,
        "email": account.email,
        "nickname": account.nickname,
        "created_at": account.created_at,
        "updated_at": account.updated_at,
    }


# 필요하면 PATCH /me 같은 것도 여기 추가 가능
# (지금은 읽기 전용 /me만 구현)
