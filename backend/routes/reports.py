from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.database import get_db
from backend.dependencies import get_current_active_user
from agent.react_agent import ReactAgent

router = APIRouter()

agent = ReactAgent()


@router.post("/", response_model=schemas.ReportResponse)
async def generate_report(
    request: schemas.ReportRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    if request.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问其他用户的报告")
    
    try:
        report_content = ""
        for chunk in agent.execute_stream(f"生成{request.report_type}报告"):
            report_content += chunk
        
        new_report = models.Report(
            user_id=request.user_id,
            report_type=request.report_type,
            content=report_content
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        
        return new_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


@router.get("/")
async def get_reports(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    reports = db.query(models.Report).filter(
        models.Report.user_id == current_user.id
    ).order_by(models.Report.generated_at.desc()).all()
    
    return [{
        "id": r.id,
        "report_type": r.report_type,
        "content": r.content,
        "generated_at": r.generated_at
    } for r in reports]


@router.get("/{report_id}", response_model=schemas.ReportResponse)
async def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此报告")
    
    return report


@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    if report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此报告")
    
    db.delete(report)
    db.commit()
    
    return {"message": "报告删除成功"}