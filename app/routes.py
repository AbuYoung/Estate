from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from app.services.statistics_service import StatisticsService
from app.services.preview_service import PreviewService
from app.services.upload_service import UploadService
from app.services.upload_service import DataUploadHistory

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        return UploadService.process_upload(request.files['file'], current_app)
    recent_uploads = DataUploadHistory.query.order_by(DataUploadHistory.upload_date.desc()).all()
    return render_template('upload.html', recent_uploads=recent_uploads)

@bp.route('/preview/<int:upload_id>')
def preview(upload_id):
    upload, properties, columns = PreviewService.get_preview_data(upload_id)
    return render_template('preview.html', 
                         upload=upload, 
                         properties=properties, 
                         columns=columns)

@bp.route('/statistics', methods=['GET'])
def statistics():
    start_date = StatisticsService.parse_date(request.args.get('start_date'))
    end_date = StatisticsService.parse_date(request.args.get('end_date'))
    
    stats = StatisticsService.get_statistics(start_date, end_date)
    return render_template('statistics.html', **stats) 