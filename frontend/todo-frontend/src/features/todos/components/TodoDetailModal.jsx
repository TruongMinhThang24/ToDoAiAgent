'use client';

import { useState, useEffect } from 'react';
import { X, Calendar, Flag, Clock, CheckCircle, AlertCircle, Edit2, Save, Ban } from 'lucide-react';

export const TodoDetailModal = ({ todo, isOpen, onClose, isLoading, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({});

  // Reset form data khi mở modal hoặc khi todo thay đổi
  useEffect(() => {
    if (todo) {
      setFormData({
        title: todo.title,
        description: todo.description || '',
        priority: todo.priority,
        due_date: todo.due_date ? todo.due_date.slice(0, 16) : '', // Format cho input datetime-local
        completed: todo.completed
      });
      setIsEditing(false); // Luôn bắt đầu ở chế độ xem
    }
  }, [todo, isOpen]);

  if (!isOpen) return null;

  const handleSave = () => {
    if (!formData.title.trim()) {
        alert('Tiêu đề không được để trống');
        return;
    }

    // ✅ FIX: Payload chuẩn cho Backend
    const payload = {
        title: formData.title.trim(),
        // Backend yêu cầu 'str', gửi null sẽ lỗi 422. Nếu rỗng thì gửi chuỗi rỗng "".
        description: formData.description ? formData.description.trim() : "", 
        priority: Number(formData.priority),
        completed: Boolean(formData.completed), // Luôn gửi true/false
    };

    // Chỉ thêm due_date nếu thực sự có giá trị
    if (formData.due_date && formData.due_date.trim() !== '') {
        payload.due_date = new Date(formData.due_date).toISOString();
    }
    // Lưu ý: Nếu user xóa ngày, không gửi due_date, Backend nhận None (đúng logic)

    console.log('Sending update payload:', payload);

    onUpdate(todo.id, payload);
    setIsEditing(false);
  };
  // Hàm helper format ngày hiển thị
  const formatDate = (dateString) => {
    if (!dateString) return 'Chưa đặt thời hạn';
    return new Date(dateString).toLocaleString('vi-VN', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  };

  const getPriorityInfo = (level) => {
    const map = {
      1: { color: 'bg-gray-100 text-gray-600', label: 'Thấp' },
      2: { color: 'bg-blue-100 text-blue-600', label: 'Bình thường' },
      3: { color: 'bg-green-100 text-green-600', label: 'Trung bình' },
      4: { color: 'bg-orange-100 text-orange-600', label: 'Cao' },
      5: { color: 'bg-red-100 text-red-600', label: 'Khẩn cấp' },
    };
    return map[level] || map[1];
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fade-in">
      <div 
        className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[85vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100 shrink-0">
          <h3 className="text-xl font-bold text-gray-800">
            {isEditing ? 'Chỉnh sửa công việc' : 'Chi tiết công việc'}
          </h3>
          <button onClick={onClose} className="p-2 text-gray-400 hover:bg-gray-100 rounded-full transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6 overflow-y-auto">
          {isLoading ? (
            <div className="flex justify-center py-10"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div></div>
          ) : todo ? (
            <>
              {/* === PHẦN TITLE & DESCRIPTION === */}
              <div>
                {isEditing ? (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Tiêu đề</label>
                      <input 
                        type="text" 
                        value={formData.title}
                        onChange={(e) => setFormData({...formData, title: e.target.value})}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none font-serif text-lg font-bold"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Mô tả</label>
                      <textarea 
                        value={formData.description}
                        onChange={(e) => setFormData({...formData, description: e.target.value})}
                        rows={5}
                        className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                      />
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <h2 className="text-2xl font-serif font-bold text-gray-900 leading-tight">{todo.title}</h2>
                      <span className={`shrink-0 px-3 py-1 rounded-full text-xs font-semibold uppercase ${todo.completed ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                        {todo.completed ? 'Đã xong' : 'Đang làm'}
                      </span>
                    </div>
                    <p className="text-gray-600 leading-relaxed whitespace-pre-wrap">
                      {todo.description || <span className="italic text-gray-400">Không có mô tả chi tiết.</span>}
                    </p>
                  </>
                )}
              </div>

              {/* === PHẦN META INFO === */}
              <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-xl">
                {/* Priority */}
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase">
                    <Flag className="w-3.5 h-3.5" /> Độ ưu tiên
                  </div>
                  {isEditing ? (
                    <select 
                      value={formData.priority}
                      onChange={(e) => setFormData({...formData, priority: Number(e.target.value)})}
                      className="w-full p-1 border border-gray-300 rounded text-sm bg-white"
                    >
                      {[1,2,3,4,5].map(lvl => (
                        <option key={lvl} value={lvl}>{lvl} - {getPriorityInfo(lvl).label}</option>
                      ))}
                    </select>
                  ) : (
                    <div className={`inline-flex items-center px-2.5 py-0.5 rounded text-sm font-medium ${getPriorityInfo(todo.priority).color}`}>
                      {getPriorityInfo(todo.priority).label} ({todo.priority})
                    </div>
                  )}
                </div>

                {/* Due Date */}
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs font-medium text-gray-500 uppercase">
                    <Calendar className="w-3.5 h-3.5" /> Thời hạn
                  </div>
                  {isEditing ? (
                    <input 
                      type="datetime-local"
                      value={formData.due_date}
                      onChange={(e) => setFormData({...formData, due_date: e.target.value})}
                      className="w-full p-1 border border-gray-300 rounded text-sm bg-white"
                    />
                  ) : (
                    <div className="text-sm font-medium text-gray-700 flex items-center gap-2">
                      {formatDate(todo.due_date)}
                    </div>
                  )}
                </div>

                {/* ID (Read-only) */}
                <div className="space-y-1 col-span-2 pt-2 border-t border-gray-200">
                  <div className="flex items-center gap-2 text-xs text-gray-400">
                    <Clock className="w-3.5 h-3.5" /> ID: #{todo.id} (Không thể sửa)
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-10 text-gray-500">
              <AlertCircle className="w-10 h-10 mx-auto mb-2 opacity-50" />
              <p>Không tìm thấy thông tin.</p>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-gray-50 border-t border-gray-100 flex justify-end gap-3 shrink-0">
          {isEditing ? (
            <>
              <button 
                onClick={() => setIsEditing(false)}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition shadow-sm"
              >
                <Ban className="w-4 h-4" /> Hủy
              </button>
              <button 
                onClick={handleSave}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition shadow-sm"
              >
                <Save className="w-4 h-4" /> Lưu thay đổi
              </button>
            </>
          ) : (
            <>
              <button 
                onClick={onClose}
                className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition shadow-sm"
              >
                Đóng
              </button>
              <button 
                onClick={() => setIsEditing(true)}
                className="flex items-center gap-2 px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 font-medium transition shadow-sm"
              >
                <Edit2 className="w-4 h-4" /> Chỉnh sửa
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};