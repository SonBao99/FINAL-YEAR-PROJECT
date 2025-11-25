# Web Dashboard Testing Guide

## 🚀 Quick Start Testing

### Prerequisites
1. **API Server Running**
   ```powershell
   # Make sure dependencies are installed
   pip install -r requirements.txt
   
   # Start the API server
   py -3 -m uvicorn attendance_api:app --reload --port 8000
   ```

2. **Open Dashboard**
   - Open `web_dashboard.html` in your web browser
   - Or navigate to `http://localhost:8000/` if the API serves it

---

## 📋 Testing Checklist

### Phase 1: Core Functionality ✅

#### Session Management
- [ ] **Create Session**
  - Click "Sessions" tab
  - Click "➕ Create Session"
  - Fill in form (course, name, dates, room)
  - Submit and verify session appears in list
  
- [ ] **Session Details**
  - Click on a session card to expand
  - Verify details show (course, times, location)
  - Test Start/Stop buttons
  
- [ ] **Session Filtering**
  - Use search box to filter sessions
  - Filter by status (Active, Scheduled, Completed)
  - Filter by course

#### Student Management
- [ ] **Enroll Student**
  - Click "Students" tab
  - Click "➕ Enroll Student"
  - Fill in student info (ID, Name, Email)
  - Upload 3-5 photos
  - Verify photos preview correctly
  - Submit and verify student appears in list
  
- [ ] **Student List**
  - Verify students display correctly
  - Test search functionality
  - Click on student to view details

#### Course Management
- [ ] **Create Course**
  - Click "Courses" tab
  - Click "➕ Create Course"
  - Fill in course details
  - Submit and verify course appears

---

### Phase 2: Enhanced Features ✅

#### Data Visualization
- [ ] **Charts Display**
  - Select a session with attendance records
  - Verify charts appear:
    - Attendance Trend (line chart)
    - Status Distribution (pie chart)
    - Attendance by Status (bar chart)
  
- [ ] **Reports Tab**
  - Click "📊 Reports" tab
  - Set date range
  - Click "Generate Report"
  - Verify statistics update
  - Verify charts display

#### Export Functionality
- [ ] **Export CSV**
  - Select a session with attendance
  - Click "📥 Export CSV"
  - Verify file downloads
  - Open file and verify data
  
- [ ] **Export Excel**
  - Click "📊 Export Excel"
  - Verify file downloads
  - Open file and verify formatting

#### Manual Entry
- [ ] **Manual Attendance**
  - Select a session
  - Click "➕ Manual Entry"
  - Select student and status
  - Submit and verify record appears

---

### Phase 3: User Experience ✅

#### Dark Mode
- [ ] **Theme Toggle**
  - Click theme toggle button (🌙/☀️)
  - Verify dark mode activates
  - Refresh page - verify theme persists
  - Toggle back to light mode

#### Navigation
- [ ] **Sidebar Navigation**
  - Click sidebar items
  - Verify active state highlights
  - Test on mobile (resize window)
  - Verify hamburger menu works
  
- [ ] **Breadcrumbs**
  - Navigate between tabs
  - Verify breadcrumbs update
  - Click breadcrumb to navigate back

#### Notifications
- [ ] **Toast Notifications**
  - Perform actions (create, update, delete)
  - Verify toast notifications appear
  - Test different types (success, error, warning, info)
  - Verify auto-dismiss works
  - Test manual close button

#### Loading States
- [ ] **Skeleton Loaders**
  - Navigate to Sessions/Students/Courses tabs
  - Verify skeleton loaders appear while loading
  - Verify content replaces skeletons

---

### Phase 4: Advanced Features ✅

#### Real-time Updates
- [ ] **WebSocket Connection**
  - Select a session
  - Verify connection status shows "🟢 Connected"
  - Check-in via kiosk or manual entry
  - Verify attendance updates automatically
  - Verify toast notification appears
  
- [ ] **Reconnection**
  - Stop API server
  - Verify status shows "🔴 Disconnected"
  - Start API server
  - Verify auto-reconnection works

#### Kiosk Mode
- [ ] **Camera Controls**
  - Select a session
  - Click "Start Camera"
  - Verify camera feed displays
  - Test camera selection dropdown
  
- [ ] **Kiosk Settings**
  - Click "⚙️ Settings"
  - Adjust confidence threshold
  - Change auto-check-in delay
  - Save settings
  - Verify settings persist
  
- [ ] **Full Screen Kiosk**
  - Click "🖥️ Full Screen"
  - Verify new window opens in fullscreen
  - Test face recognition in kiosk mode
  - Verify check-ins work

#### Bulk Operations
- [ ] **Bulk Enroll**
  - Click FAB (+) button
  - Click "📦 Bulk Operations"
  - Select "Bulk Enroll Students"
  - Upload CSV file (see sample below)
  - Verify preview shows
  - Submit and verify students enrolled
  
- [ ] **Bulk Create Sessions**
  - Select "Bulk Create Sessions"
  - Fill in form (pattern, count, dates)
  - Submit and verify sessions created
  
- [ ] **Bulk Mark Attendance**
  - Select a session
  - Select "Bulk Mark Attendance"
  - Check multiple students
  - Select status
  - Submit and verify attendance marked

---

## 🧪 Test Data

### Sample CSV for Bulk Enroll
Create a file `bulk_enroll.csv`:
```csv
student_id,name,email
STU001,John Doe,john@example.com
STU002,Jane Smith,jane@example.com
STU003,Bob Johnson,bob@example.com
```

### Test Scenarios

1. **End-to-End Flow**
   - Create a course
   - Enroll 2-3 students with photos
   - Create a session
   - Start the session
   - Check-in students (via kiosk or manual)
   - View attendance records
   - Export data
   - Generate report

2. **Error Handling**
   - Try to create session without course
   - Try to enroll student with duplicate ID
   - Try to check-in without active session
   - Verify error messages display correctly

3. **Responsive Design**
   - Resize browser window
   - Test on mobile viewport (< 768px)
   - Verify sidebar collapses
   - Verify layout adapts

---

## 🐛 Common Issues & Solutions

### Issue: Dashboard doesn't load
- **Solution**: Make sure API server is running on port 8000
- Check browser console for errors

### Issue: WebSocket not connecting
- **Solution**: Verify API server is running
- Check if session is selected
- Check browser console for WebSocket errors

### Issue: Camera not working
- **Solution**: Grant camera permissions in browser
- Check if camera is being used by another app
- Try different camera from dropdown

### Issue: Charts not displaying
- **Solution**: Make sure Chart.js CDN loaded
- Check browser console for errors
- Verify attendance data exists

### Issue: Export not working
- **Solution**: Check browser download settings
- Verify SheetJS library loaded
- Check browser console for errors

---

## 📊 Expected Results

### After Complete Test:
- ✅ All tabs functional
- ✅ Create/Read/Update operations work
- ✅ Charts display correctly
- ✅ Export functions work
- ✅ Dark mode toggles
- ✅ Notifications appear
- ✅ WebSocket connects
- ✅ Kiosk mode works
- ✅ Bulk operations complete

---

## 🔍 Browser Console Testing

Open browser DevTools (F12) and check:
- No JavaScript errors
- Network requests succeed (200 status)
- WebSocket connection established
- No CORS errors
- Console logs for debugging

---

## 📝 Test Report Template

**Date**: _____________
**Tester**: _____________
**Browser**: _____________
**OS**: _____________

**Issues Found**:
1. 
2. 
3. 

**Features Working**:
- [ ] Phase 1: Core Functionality
- [ ] Phase 2: Enhanced Features
- [ ] Phase 3: User Experience
- [ ] Phase 4: Advanced Features

**Overall Status**: ⬜ Pass ⬜ Fail ⬜ Needs Fixes

---

**Happy Testing! 🎉**


