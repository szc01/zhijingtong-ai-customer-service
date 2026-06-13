"""
智净通智能客服系统 - 测试运行脚本
运行所有单元测试并生成报告
"""
import subprocess
import sys


def run_tests():
    """运行测试"""
    print("=" * 50)
    print("智净通智能客服系统 - 单元测试")
    print("=" * 50)
    
    # 运行pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    
    if result.stderr:
        print("错误输出:")
        print(result.stderr)
    
    print("=" * 50)
    
    if result.returncode == 0:
        print("✅ 所有测试通过!")
    else:
        print("❌ 测试失败，请检查错误信息")
    
    return result.returncode


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)