#!/bin/bash
# Cleanup unnecessary files from codebase
# Run: bash cleanup.sh

echo "🧹 Cleaning up codebase..."
echo ""

# Delete duplicate/old scripts
echo "Deleting duplicate/old scripts..."
rm -f attendance_api_simple.py kiosk_simple.py start.py
rm -f enroll_students.py display_image.py face_detection.py
rm -f realtime_face_detect.py check_database.py

# Delete quick test scripts
echo "Deleting quick test scripts..."
rm -f quick_enroll_test.py quick_enroll_me.py
rm -f quick_session_test.py create_session_quick.py

# Delete setup scripts
echo "Deleting setup scripts..."
rm -f setup_sample_data.py setup_environment.py setup.py
rm -f install_dependencies.py

# Delete test files
echo "Deleting test files..."
rm -f test_button_functions.html test_web_dashboard.py
rm -f test_dashboard_setup.py test_camera.py test_api_startup.py
rm -f test_checkin.py test_liveness.py

# Delete old documentation
echo "Deleting old documentation..."
rm -f TODAY_PLAN.md TODAY_SUMMARY.md TODAY_SCHEDULE_SUMMARY.md
rm -f SESSION_NOTES.md NEXT_STEPS_TODAY.md
rm -f RECENT_WORK_REPORT.md PROGRESS_SUMMARY.md SCHEDULE_PROGRESS.md
rm -f MILESTONE_1_COMPLETE.md MILESTONE_2_PROGRESS.md
rm -f LIVE_CAMERA_TEST_SUMMARY.md TEST_RESULTS.md
rm -f WEB_DASHBOARD_TEST_RESULTS.md

# Delete duplicate deployment docs
echo "Deleting duplicate deployment docs..."
rm -f QUICK_DEPLOYMENT.md QUICK_RENDER_DEPLOY.md README_RENDER.md
rm -f VERCEL_DEPLOYMENT.md vercel.json

# Delete old files
echo "Deleting old files..."
rm -f requirements_basic.txt todo.txt

# Delete Vercel-specific files (if not using)
echo "Deleting Vercel-specific files..."
rm -rf api/

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Files deleted. Review CODEBASE_REVIEW.md for details."

