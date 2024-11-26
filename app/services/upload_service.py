import os
import pandas as pd
from werkzeug.utils import secure_filename
from app import db
from app.models import Property, DataUploadHistory
from datetime import datetime
import pytz
from flask import jsonify, Response, current_app
import json

class UploadService:
    @staticmethod
    def get_current_time():
        """获取当前北京时间"""
        beijing_tz = pytz.timezone('Asia/Shanghai')
        return datetime.now(beijing_tz)

    @staticmethod
    def allowed_file(filename):
        """检查文件类型是否允许"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx'}

    @staticmethod
    def process_upload(file, app):
        """处理文件上传"""
        if not file:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if not UploadService.allowed_file(file.filename):
            return jsonify({'success': False, 'message': '只允许上传 .xlsx 格式的文件'})

        def generate():
            file_path = None
            try:
                # 发送上传开始消息
                yield json.dumps({
                    'phase': 'upload',
                    'progress': 0,
                    'message': '开始上传文件...'
                }) + '\n'

                # 保存文件
                original_filename = file.filename
                safe_filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_filename)
                file.save(file_path)

                yield json.dumps({
                    'phase': 'upload',
                    'progress': 100,
                    'message': '文件上传完成，开始处理数据...'
                }) + '\n'

                # 创建上传记录
                upload_record = DataUploadHistory(
                    filename=original_filename,
                    upload_date=UploadService.get_current_time(),
                    record_count=0
                )
                db.session.add(upload_record)
                db.session.commit()

                # 读取Excel文件
                df = pd.read_excel(file_path)
                total_rows = len(df)
                processed_rows = 0
                batch_size = 1000

                yield json.dumps({
                    'phase': 'process',
                    'progress': 0,
                    'message': f'开始处理 {total_rows} 条数据...'
                }) + '\n'

                # 分批处理数据
                for i in range(0, total_rows, batch_size):
                    batch_df = df.iloc[i:i+batch_size]
                    
                    # 处理这一批数据
                    for _, row in batch_df.iterrows():
                        # 处理单条数据的代码
                        property_data = Property(
                            upload_id=upload_record.id,
                            office_id=str(row['办件号']) if pd.notna(row['办件号']) else None,
                            file_id=str(row['FILEID']) if pd.notna(row['FILEID']) else None,
                            control_id=str(row['CONTROLID']) if pd.notna(row['CONTROLID']) else None,
                            step_id=str(row['STEPID']) if pd.notna(row['STEPID']) else None,
                            business_type=str(row['业务类型']) if pd.notna(row['业务类型']) else None,
                            receive_date=UploadService.parse_datetime(row['新件收件日期']),
                            presale_permit_no=str(row['预售证编号']) if pd.notna(row['预售证编号']) else None,
                            presale_reg_no=str(row['预售登记证明书号']) if pd.notna(row['预售登记证明书号']) else None,
                            project_name=str(row['项目名称']) if pd.notna(row['项目名称']) else None,
                            developer_name=str(row['开发企业名称']) if pd.notna(row['开发企业名称']) else None,
                            district=str(row['所在区']) if pd.notna(row['所在区']) else None,
                            address=str(row['登记坐落']) if pd.notna(row['登记坐落']) else None,
                            residential_units=UploadService.parse_int(row['住宅套数']),
                            building_area=UploadService.parse_float(row['建筑面积']),
                            address_abbr=str(row['地址缩写']) if pd.notna(row['地址缩写']) else None,
                            house_area=UploadService.parse_float(row['房屋建筑面积']),
                            inner_area=UploadService.parse_float(row['套内建筑面积']),
                            structure=str(row['建筑结构']) if pd.notna(row['建筑结构']) else None,
                            house_type=str(row['户型']) if pd.notna(row['户型']) else None,
                            orientation=str(row['朝向']) if pd.notna(row['朝向']) else None,
                            purpose=str(row['用途']) if pd.notna(row['用途']) else None,
                            building_no=str(row['楼号']) if pd.notna(row['楼号']) else None,
                            room_no=str(row['房号']) if pd.notna(row['房号']) else None,
                            total_floors=UploadService.parse_int(row['总层数']),
                            is_available=str(row['是否可售']) if pd.notna(row['是否可售']) else None,
                            current_floor=UploadService.parse_int(row['所在层']),
                            presale_price=UploadService.parse_float(row['预售单价']),
                            sale_status=str(row['实际销售状态']) if pd.notna(row['实际销售状态']) else None,
                            sale_price=UploadService.parse_float(row['销售单价']),
                            total_price=UploadService.parse_float(row['销售总价']),
                            contract_date=UploadService.parse_datetime(row['合同签订时间']),
                            id_number=str(row['证件号码']) if pd.notna(row['证件号码']) else None,
                            first_cert_date=UploadService.parse_datetime(row['首次发证时间']),
                            archive_time=UploadService.parse_datetime(row['ARCHIVETIME']),
                            old_system_id=str(row['老系统办件号']) if pd.notna(row['老系统办件号']) else None,
                            modify_time=UploadService.parse_datetime(row['MODIFYTIME']),
                            storage_status=str(row['库状态']) if pd.notna(row['库状态']) else None,
                            property_nature=str(row['房屋性质']) if pd.notna(row['房屋性质']) else None,
                            fee_amount=UploadService.parse_float(row['收费金额'])
                        )
                        db.session.add(property_data)
                        processed_rows += 1
                        
                        # 每处理100条数据更新一次进度
                        if processed_rows % 100 == 0:
                            progress = int((processed_rows / total_rows) * 100)
                            db.session.commit()  # 每100条提交一次
                            yield json.dumps({
                                'phase': 'process',
                                'progress': progress,
                                'message': f'正在处理数据... ({processed_rows}/{total_rows})'
                            }) + '\n'
                    
                    # 每批次提交一次
                    db.session.commit()

                # 更新记录数量
                upload_record.record_count = processed_rows
                db.session.commit()

                # 删除临时文件
                if os.path.exists(file_path):
                    os.remove(file_path)

                yield json.dumps({
                    'phase': 'complete',
                    'progress': 100,
                    'message': f'处理完成！共导入 {processed_rows} 条记录。',
                    'success': True
                }) + '\n'

            except Exception as e:
                db.session.rollback()
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                yield json.dumps({
                    'phase': 'error',
                    'message': f'处理失败：{str(e)}',
                    'success': False
                }) + '\n'

        return Response(generate(), mimetype='text/event-stream')

    @staticmethod
    def parse_datetime(value):
        """安全地解析日期时间"""
        if pd.isna(value) or value == '' or value is None:
            return None
        try:
            if isinstance(value, str):
                dt = pd.to_datetime(value, format='%Y/%m/%d')
            else:
                dt = pd.to_datetime(value)
            if pd.notna(dt):
                return dt.tz_localize(pytz.UTC).tz_convert(pytz.timezone('Asia/Shanghai'))
            return None
        except:
            return None

    @staticmethod
    def parse_float(value):
        """安全地解析浮点数"""
        if pd.isna(value) or value == '' or value is None:
            return None
        try:
            return float(value)
        except:
            return None

    @staticmethod
    def parse_int(value):
        """安全地解析整数"""
        if pd.isna(value) or value == '' or value is None:
            return None
        try:
            return int(float(value))
        except:
            return None

    @staticmethod
    def process_excel_data(df, upload_id):
        """处理Excel数据"""
        # ... Excel处理代码保持不变 ...
        pass