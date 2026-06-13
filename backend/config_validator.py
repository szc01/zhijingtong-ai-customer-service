"""
智净通智能客服系统 - 配置验证模块
验证环境配置和必要的环境变量
"""
import os
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ConfigValidationResult:
    """配置验证结果"""
    is_valid: bool
    missing_configs: List[str]
    warnings: List[str]


def validate_environment() -> ConfigValidationResult:
    """
    验证环境配置
    
    检查：
    - 必要的环境变量
    - 配置文件是否存在
    - API密钥是否设置
    
    Returns:
        ConfigValidationResult: 验证结果
    """
    missing_configs = []
    warnings = []
    
    # 检查必要的环境变量
    required_env_vars = [
        ("SECRET_KEY", "JWT认证密钥"),
    ]
    
    for var_name, description in required_env_vars:
        value = os.getenv(var_name)
        if not value or value == f"your-{var_name.lower()}-here-change-in-production":
            missing_configs.append(f"{var_name} ({description})")
    
    # 检查配置文件
    config_files = [
        "config/rag.yml",
        "config/chroma.yml",
        "config/prompts.yml",
        "config/agent.yml",
    ]
    
    for config_file in config_files:
        if not os.path.exists(config_file):
            missing_configs.append(f"配置文件: {config_file}")
    
    # 检查提示词文件
    prompt_files = [
        "prompts/main_prompt.txt",
        "prompts/rag_summarize.txt",
        "prompts/report_prompt.txt",
    ]
    
    for prompt_file in prompt_files:
        if not os.path.exists(prompt_file):
            missing_configs.append(f"提示词文件: {prompt_file}")
    
    # 检查数据目录
    data_dir = "data"
    if not os.path.exists(data_dir):
        warnings.append(f"数据目录 '{data_dir}' 不存在，将自动创建")
    
    # 检查DashScope API Key（通义千问）
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    if not dashscope_key:
        warnings.append("DASHSCOPE_API_KEY 未设置，LLM服务可能无法正常工作")
    
    return ConfigValidationResult(
        is_valid=len(missing_configs) == 0,
        missing_configs=missing_configs,
        warnings=warnings
    )


def check_config_on_startup():
    """
    启动时检查配置
    
    如果配置缺失，打印警告信息
    """
    result = validate_environment()
    
    if not result.is_valid:
        print("\n" + "=" * 50)
        print("⚠️  配置检查警告")
        print("=" * 50)
        print("\n缺失配置项:")
        for item in result.missing_configs:
            print(f"  ❌ {item}")
        print("\n请检查并配置上述项目后再启动服务")
        print("=" * 50 + "\n")
    
    if result.warnings:
        print("\n" + "=" * 50)
        print("📋 配置提示")
        print("=" * 50)
        for warning in result.warnings:
            print(f"  ⚠️  {warning}")
        print("=" * 50 + "\n")
    
    return result.is_valid


def get_config_summary() -> dict:
    """
    获取配置摘要
    
    Returns:
        dict: 配置状态摘要
    """
    result = validate_environment()
    return {
        "is_valid": result.is_valid,
        "missing_count": len(result.missing_configs),
        "warning_count": len(result.warnings),
        "missing_configs": result.missing_configs,
        "warnings": result.warnings
    }