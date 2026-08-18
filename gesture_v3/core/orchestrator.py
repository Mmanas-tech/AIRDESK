
import cv2
import time
import pyautogui
from gesture_v3 import engine_constants
from gesture_v3.perception.landmark_detector import HandTracker
from gesture_v3.perception.jitter_filter import OneEuroFilter
from gesture_v3.intent.gesture_decoder import GestureClassifier
from gesture_v3.control.cursor_engine import PhysicsCursor
from gesture_v3.ui.holographic_overlay import CinematicHUD

class SystemController:
    """
    Core Application Loop (V3)
    Orchestrates: Camera -> Tracker -> Smoother -> Intent -> Physics -> UI -> Display
    """
    def __init__(self):
        self.running = True
        self.cap = cv2.VideoCapture(engine_constants.CAMERA_INDEX)

        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera. Check connection and permissions.")

        # Setup Camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, engine_constants.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, engine_constants.FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, engine_constants.TARGET_FPS)

        # Modules
        self.tracker = HandTracker()
        self.start_time = time.time()

        # State (initialized properly, not lazily)
        self.prev_hand_x = None
        self.prev_hand_y = None
        self.drag_active = False
        self.last_toggle_time = 0
        self.last_click_time = 0
        self.last_scroll_y = None

    def run(self):
        print(f"[{engine_constants.APP_NAME}] System Initialized. Press 'Q' to Quit.")

        smoother = OneEuroFilter(
            time.time(), [0.5, 0.5],
            min_cutoff=engine_constants.ONE_EURO_MIN_CUTOFF,
            beta=engine_constants.ONE_EURO_BETA
        )
        classifier = GestureClassifier()
        cursor = PhysicsCursor()
        hud = CinematicHUD()

        last_time = time.time()

        try:
            while self.running:
                # Time Delta
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time

                success, img = self.cap.read()
                if not success:
                    print("Camera read failed. Retrying...")
                    time.sleep(0.1)
                    continue

                # 1. Flip & Color correction
                img = cv2.flip(img, 1)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # 2. Perception (Tracking)
                frame_timestamp_ms = (current_time - self.start_time) * 1000

                # Safety Check: Low FPS
                fps = 1 / dt if dt > 0 else 0
                if fps < engine_constants.FAILSAFE_FPS and (current_time - self.start_time) > 2.0:
                    screen_w, screen_h = engine_constants.get_screen_size()
                    cv2.putText(img, "SAFETY PAUSE: LOW FPS",
                                (int(screen_w) // 2 - 150, int(screen_h) // 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.imshow(engine_constants.APP_NAME, img)
                    key = cv2.waitKey(1)
                    if key == ord('q'):
                        self.running = False
                    continue

                try:
                    detection_result = self.tracker.process(img_rgb, frame_timestamp_ms)
                except Exception as e:
                    print(f"Tracking error: {e}")
                    detection_result = None

                hand_landmarks = None
                delta_x, delta_y = 0.0, 0.0
                state = "IDLE"
                confidence = 0.0

                if detection_result and detection_result.hand_landmarks:
                    hand_landmarks = detection_result.hand_landmarks[0]

                    # --- V6 RELATIVE TRACKING ---
                    raw_point = hand_landmarks[5]
                    norm_x, norm_y = raw_point.x, raw_point.y

                    # 3. Smoothing
                    filtered_pos = smoother(current_time, [norm_x, norm_y])
                    curr_x, curr_y = filtered_pos[0], filtered_pos[1]

                    # Calculate Delta
                    if self.prev_hand_x is not None:
                        delta_x = curr_x - self.prev_hand_x
                        delta_y = curr_y - self.prev_hand_y

                    self.prev_hand_x = curr_x
                    self.prev_hand_y = curr_y

                    # 4. Intent Classification
                    state, meta = classifier.process(hand_landmarks)
                    raw_state = state
                    confidence = meta.get("confidence", 0.0)

                    # --- V6 STATE MACHINE ---
                    current_time_loop = time.time()

                    # 1. DRAG TOGGLE LOGIC (FIST)
                    if state == "FIST":
                        if (current_time_loop - self.last_toggle_time) > engine_constants.DRAG_TOGGLE_COOLDOWN:
                            self.drag_active = not self.drag_active
                            self.last_toggle_time = current_time_loop

                            try:
                                if self.drag_active:
                                    pyautogui.mouseDown()
                                else:
                                    pyautogui.mouseUp()
                            except pyautogui.FailSafeException:
                                pass

                    # 2. EXECUTE ACTIONS BASED ON STATE & TOGGLE

                    # A. DRAG MODE (Active)
                    if self.drag_active:
                        state = "DRAG_ACTIVE"

                        if raw_state in ("MOVE", "IDLE", "FIST"):
                            cursor.update_relative(delta_x, delta_y, dt)

                    # B. NORMAL MODE (Not Dragging)
                    else:
                        if state == "MOVE":
                            cursor.update_relative(delta_x, delta_y, dt)

                        elif state == "CLICK_LEFT":
                            if (current_time_loop - self.last_click_time) > engine_constants.CLICK_COOLDOWN:
                                try:
                                    pyautogui.click()
                                except pyautogui.FailSafeException:
                                    pass
                                self.last_click_time = current_time_loop
                                cv2.circle(img, (int(norm_x * engine_constants.FRAME_WIDTH),
                                                 int(norm_y * engine_constants.FRAME_HEIGHT)),
                                           50, engine_constants.COLOR_CLICK, 4)

                        elif state == "CLICK_RIGHT":
                            if (current_time_loop - self.last_click_time) > engine_constants.CLICK_COOLDOWN:
                                try:
                                    pyautogui.rightClick()
                                except pyautogui.FailSafeException:
                                    pass
                                self.last_click_time = current_time_loop

                        elif state == "SCROLL":
                            if self.last_scroll_y is not None:
                                dy = norm_y - self.last_scroll_y
                                if abs(dy) > engine_constants.SCROLL_DEADZONE:
                                    try:
                                        scroll_amount = int(-dy * engine_constants.SCROLL_SPEED * 100)
                                        pyautogui.scroll(scroll_amount)
                                    except pyautogui.FailSafeException:
                                        pass
                            self.last_scroll_y = norm_y
                        else:
                            self.last_scroll_y = None

                    # 5. UI Layer
                    hud.draw(img, hand_landmarks, state, confidence)

                else:
                    # HAND LOST SAFETY
                    if self.drag_active:
                        try:
                            pyautogui.mouseUp()
                        except pyautogui.FailSafeException:
                            pass
                        self.drag_active = False
                        print("Hand lost. Safety Drop.")

                    # Reset Delta Reference
                    self.prev_hand_x = None
                    self.prev_hand_y = None

                    classifier.process(None)
                    hud.draw(img, None, "IDLE", 0.0)

                # 7. System Info
                cv2.putText(img, f"AIRDESK  |  FPS: {int(fps)}", (20, 30),
                            cv2.FONT_HERSHEY_PLAIN, 1, (200, 255, 200), 1)

                # 8. Display
                cv2.imshow(engine_constants.APP_NAME, img)

                # 9. Inputs
                key = cv2.waitKey(1)
                if key == ord('q'):
                    self.running = False

        finally:
            self.cap.release()
            cv2.destroyAllWindows()
