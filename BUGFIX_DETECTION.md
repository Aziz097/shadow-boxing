# Bug Fixes - Hitbox & Blocking Detection

## Date: November 10, 2025

## Issues Reported:
1. ❌ Tidak bisa hit punch bag
2. ❌ Blocking detection ada bug

---

## Root Causes Identified:

### Issue 1: Velocity Detection Too Strict
**Problem**: 
- Added `MIN_PUNCH_VELOCITY = 500` check yang terlalu ketat
- Slow/medium punches tidak terdeteksi
- Hand velocity calculation unreliable karena frame timing

**Solution**:
- ✅ Remove velocity requirement completely
- ✅ Detection based ONLY on hand landmarks position
- ✅ Check 7 hand points: wrist, 4 knuckles, 2 fingertips
- ✅ Lebih responsive, semua punch speed terdeteksi

**Code Changed**: `game/game_manager.py` -> `check_hitbox_collisions()`

---

### Issue 2: Hitbox Position Inconsistency
**Problem**:
- `generate_hitboxes()` creates position as TOP-LEFT corner
- `draw_hitbox()` expected CENTER position
- Collision detection using top-left, but visual was offset

**Solution**:
- ✅ Updated `draw_hitbox()` to accept TOP-LEFT position
- ✅ Calculate center internally for visual rendering
- ✅ Collision and visual now aligned perfectly

**Code Changed**: `systems/visual_effects.py` -> `draw_hitbox()`

---

### Issue 3: Blocking Detection Too Sensitive
**Problem**:
- Distance threshold 150 pixels was too large
- Player hands detected as blocking even when far from face
- Console spam with "BLOCKING!" messages

**Solutions**:
- ✅ Reduced distance threshold from 150 to 100 pixels
- ✅ Added print throttling (0.5s between messages)
- ✅ More accurate blocking - must be closer to face

**Code Changed**: `game/game_manager.py` -> `check_defense()`

---

### Issue 4: Defense Detection Methods
**Enhanced with 2 fallback methods**:

1. **Primary Method**: Nose-to-Wrist Distance
   - Uses pose landmark (nose) as reference
   - Calculates Euclidean distance to hand wrist
   - Threshold: < 100 pixels

2. **Fallback Method**: Position-Based
   - If no pose detected, use screen regions
   - Check if wrist in upper-center area
   - Region: center ±25% width, upper 40% ±20% height

**Benefits**:
- Works even if face not detected
- More robust across different camera angles
- Less false positives

---

## Files Modified:

### 1. `game/game_manager.py`
**Changes**:
- Simplified `check_hitbox_collisions()` - removed velocity check
- Improved `check_defense()` with distance-based detection
- Added console spam prevention
- Increased hitbox check points from 4 to 7

### 2. `systems/visual_effects.py`
**Changes**:
- Fixed `draw_hitbox()` position handling (top-left vs center)
- Punching bag now renders correctly aligned with collision
- Glow effect properly centered

### 3. `config.py`
**Changes**:
- Increased `HITBOX_SIZE` from 100 to 120 pixels
- Easier to hit targets

---

## Testing Results:

### Before Fixes:
❌ Hitbox tidak bisa di-hit  
❌ Console tidak ada "HIT!" messages  
❌ Blocking terdeteksi terus-menerus  
❌ Punch bag visual tidak align dengan hitbox  

### After Fixes:
✅ Hitbox detection working perfectly  
✅ Multiple "HIT!" confirmations in console  
✅ Blocking detection accurate (distance < 100px)  
✅ Punch bag visual aligned with collision  
✅ Sound plays on every hit  
✅ Round transitions working  

---

## Console Output Evidence:
```
Generated 4 hitboxes
HIT! Hitbox at (826, 303)
HIT! Hitbox at (674, 238)
BLOCKING!
BLOCKED!
HIT! Hitbox at (815, 384)
HIT! Hitbox at (353, 220)
...
Round 1 ended!
Rest period before round 2
```

---

## Configuration Summary:

```python
# config.py
HITBOX_SIZE = 120  # Increased for easier hitting
MIN_PUNCH_VELOCITY = 500  # Not used anymore

# game_manager.py
BLOCKING_DISTANCE = 100  # Distance threshold (pixels)
defense_memory_duration = 0.6  # Block memory (seconds)
```

---

## Hand Landmarks Used:

**Hitbox Detection** (7 points):
- 0: Wrist
- 5: Index knuckle
- 9: Middle knuckle
- 13: Ring knuckle
- 17: Pinky knuckle
- 8: Index tip
- 12: Middle tip

**Defense Detection** (1 point):
- 0: Wrist (checked against nose position)

---

## Key Improvements:

1. **Simpler = Better**
   - Removed complex velocity tracking
   - Direct position-based detection
   - More reliable and responsive

2. **Multiple Fallbacks**
   - Primary: nose-distance detection
   - Fallback: region-based detection
   - Always works in various conditions

3. **Visual Consistency**
   - Fixed position coordinate system
   - Hitbox visual matches collision area
   - Punching bag renders at correct position

4. **Better UX**
   - Larger hitbox (120px)
   - Immediate audio feedback
   - Reduced console spam

---

**Status**: All bugs fixed and tested ✅

**Game is now fully playable!** 🥊
