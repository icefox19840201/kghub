from fastapi import Request, UploadFile, File
from fastapi.responses import JSONResponse
import os
import uuid
from datetime import datetime
from core.base.viewbase import BaseView
class Default(BaseView):
    def default_page(self,request:Request):
        return self.template.TemplateResponse('main.html',{'request':request})
    def right_page(self,request:Request):
        return self.template.TemplateResponse('knowledge_query.html',{'request':request})
    def left_page(self, request: Request):
        return self.template.TemplateResponse('menu.html', {'request': request})
    def doc_qa(self,request:Request):
        return self.template.TemplateResponse('doc_qa.html',{'request':request})
    def spider_data(self,request:Request):
        return self.template.TemplateResponse('spider_data.html',{'request':request})
    def nlp_query(self,request:Request):
        return self.template.TemplateResponse('text-to-sq-queryl.html',{'request':request})
    def doc_management(self,request:Request):
        return self.template.TemplateResponse('doc_management.html',{'request':request})
    def doc_import(self,request:Request):
        return self.template.TemplateResponse('doc_import.html',{'request':request})
    def audio_to_text(self,request:Request):
        return self.template.TemplateResponse('audio_to_text.html',{'request':request})
    def tag_management(self,request:Request):
        return self.template.TemplateResponse('tag_management.html',{'request':request})
    def data_backup(self,requet:Request):
        return self.template.TemplateResponse('data_backup.html',{'request':requet})
    def system_settings(self,request:Request):
        return self.template.TemplateResponse('system_settings.html',{'request':request})
    def right_settings(self,request:Request):
        return self.template.TemplateResponse('right_settings.html',{'request':request})

    async def file_upload(self, request: Request, file: UploadFile = File(...)):
        '''
        文件上传
        :param request:
        :param file: 上传的文件
        :return:
        '''
        try:
            # 验证文件类型
            print('上传')
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.xls', '.html', '.md']
            file_ext = os.path.splitext(file.filename)[1].lower()
            
            if file_ext not in allowed_extensions:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": f"不支持的文件类型。支持的格式: {', '.join(allowed_extensions)}"}
                )
            
            # 验证文件大小 (最大100MB)
            if file.size > 100 * 1024 * 1024:
                return JSONResponse(
                    status_code=400,
                    content={"success": False, "message": "文件大小不能超过100MB"}
                )
            
            # 创建上传目录
            upload_dir = "uploads"
            os.makedirs(upload_dir, exist_ok=True)
            
            # 生成唯一文件名
            unique_filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # 保存文件
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # 这里可以添加文档解析和向量化的逻辑
            # 暂时返回成功信息
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "message": "文件上传成功",
                    "data": {
                        "filename": file.filename,
                        "size": file.size,
                        "type": file_ext,
                        "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "file_path": file_path
                    }
                }
            )
            
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": f"文件上传失败: {str(e)}"}
            )