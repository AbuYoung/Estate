from app.models import Property, DataUploadHistory

class PreviewService:
    @staticmethod
    def get_column_names():
        """获取字段名称映射"""
        return {
            'office_id': '办件号',
            'file_id': 'FILEID',
            'control_id': 'CONTROLID',
            # ... 其他字段映射
        }

    @staticmethod
    def get_preview_data(upload_id):
        """获取预览数据"""
        upload = DataUploadHistory.query.get_or_404(upload_id)
        properties = Property.query.filter_by(upload_id=upload_id).limit(10).all()
        
        column_names = PreviewService.get_column_names()
        columns = [(name, column_names.get(name, name)) for name in [
            column.name for column in Property.__table__.columns 
            if column.name not in ['id', 'upload_id', 'created_at']
        ]]
        
        return upload, properties, columns 