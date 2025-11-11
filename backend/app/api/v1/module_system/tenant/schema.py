# -*- coding: utf-8 -*-

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.base_schema import BaseSchema


class TenantCreateSchema(BaseModel):
    """新增模型"""
    name: str = Field(..., max_length=50, description='租户名称')
    status: bool = Field(True, description="是否启用(True:启用 False:禁用)")
    description: Optional[str] = Field(default=None, max_length=255, description="描述")

    @field_validator('name')
    @classmethod
    def _validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('名称不能为空')
        return v


class TenantUpdateSchema(TenantCreateSchema):
    """更新模型"""
    ...


class TenantOutSchema(TenantCreateSchema, BaseSchema):
    """响应模型"""
    model_config = ConfigDict(from_attributes=True)
