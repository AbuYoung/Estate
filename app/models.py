from app import db
from datetime import datetime

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # 基础信息
    office_id = db.Column(db.String(50), comment='办件号')
    file_id = db.Column(db.String(50), comment='FILEID')
    control_id = db.Column(db.String(50), comment='CONTROLID')
    step_id = db.Column(db.String(50), comment='STEPID')
    business_type = db.Column(db.String(50), comment='业务类型')
    receive_date = db.Column(db.DateTime, comment='新件收件日期')
    
    # 预售信息
    presale_permit_no = db.Column(db.String(50), comment='预售证编号')
    presale_reg_no = db.Column(db.String(50), comment='预售登记证明书号')
    
    # 项目信息
    project_name = db.Column(db.String(100), comment='项目名称')
    developer_name = db.Column(db.String(100), comment='开发企业名称')
    district = db.Column(db.String(50), comment='所在区')
    address = db.Column(db.String(200), comment='登记坐落')
    address_abbr = db.Column(db.String(100), comment='地址缩写')
    
    # 房屋信息
    residential_units = db.Column(db.Integer, comment='住宅套数')
    building_area = db.Column(db.Float, comment='建筑面积')
    house_area = db.Column(db.Float, comment='房屋建筑面积')
    inner_area = db.Column(db.Float, comment='套内建筑面积')
    structure = db.Column(db.String(50), comment='建筑结构')
    house_type = db.Column(db.String(50), comment='户型')
    orientation = db.Column(db.String(50), comment='朝向')
    purpose = db.Column(db.String(50), comment='用途')
    building_no = db.Column(db.String(50), comment='楼号')
    room_no = db.Column(db.String(50), comment='房号')
    total_floors = db.Column(db.Integer, comment='总层数')
    current_floor = db.Column(db.Integer, comment='所在层')
    
    # 销售信息
    is_available = db.Column(db.String(10), comment='是否可售')
    presale_price = db.Column(db.Float, comment='预售单价')
    sale_status = db.Column(db.String(50), comment='实际销售状态')
    sale_price = db.Column(db.Float, comment='销售单价')
    total_price = db.Column(db.Float, comment='销售总价')
    contract_date = db.Column(db.DateTime, comment='合同签订时间')
    
    # 其他信息
    id_number = db.Column(db.String(50), comment='证件号码')
    first_cert_date = db.Column(db.DateTime, comment='首次发证时间')
    archive_time = db.Column(db.DateTime, comment='ARCHIVETIME')
    old_system_id = db.Column(db.String(50), comment='老系统办件号')
    modify_time = db.Column(db.DateTime, comment='MODIFYTIME')
    storage_status = db.Column(db.String(50), comment='库状态')
    property_nature = db.Column(db.String(50), comment='房屋性质')
    
    # 收费信息
    fee_amount = db.Column(db.Float, comment='收费金额')
    
    # 上传记录关联
    upload_id = db.Column(db.Integer, db.ForeignKey('data_upload_history.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Property {self.project_name} - {self.building_no}-{self.room_no}>'

class DataUploadHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    record_count = db.Column(db.Integer, nullable=False)
    properties = db.relationship('Property', backref='upload_history', lazy=True)
    
    def __repr__(self):
        return f'<DataUpload {self.filename} - {self.upload_date}>' 