# New Features: Dodge Mechanics & Side Hitboxes

## Date: November 10, 2025

## Features Implemented:

---

### 1. ✅ **Dodge Mechanics - Red Dot Can Be Avoided**

**Problem**: 
- Red dot (enemy attack) tidak bisa dihindari
- Player hanya bisa block dengan tangan
- Tidak ada mechanics untuk menggeser kepala/body

**Solution**:
Implemented full dodge detection system:

#### **How It Works:**
1. **Initial Position Tracking**
   - Saat enemy attack warning muncul, sistem save posisi landmark target (red dot)
   - Tracking menggunakan pose landmark (0-10: nose, shoulders, etc.)

2. **Movement Detection**
   - Setiap frame, hitung jarak antara posisi awal vs posisi sekarang
   - Gunakan Euclidean distance formula: `√((x₂-x₁)² + (y₂-y₁)²)`

3. **Dodge Success Criteria**
   - Distance moved > `DODGE_DISTANCE_THRESHOLD` (80 pixels)
   - Dodge state persist for `DODGE_MEMORY_DURATION` (0.3 seconds)

4. **Attack Avoidance**
   - Enemy attack misses if: `is_blocking OR is_dodging`
   - Console shows "DODGED!" vs "BLOCKED!"

#### **Configuration:**
```python
# config.py
DODGE_DISTANCE_THRESHOLD = 80  # Minimum movement (pixels)
DODGE_MEMORY_DURATION = 0.3    # Dodge state duration (seconds)
```

#### **Code Added:**
- `check_dodge(current_time)` method in `game_manager.py`
- `target_initial_pos` tracking variable
- `last_dodge_time` memory system
- Updated `check_defense()` to work alongside dodge

---

### 2. ✅ **Hitbox Positioning - Left & Right Only**

**Problem**:
- Hitbox spawn di semua area termasuk tengah (body area)
- Body/torso bisa kena hitbox = false positive
- Tidak realistic untuk boxing game

**Solution**:
Hitbox generation dengan zone exclusion:

#### **Zone System:**
```
|---- LEFT ZONE ----|---- CENTER (BODY) ----|---- RIGHT ZONE ----|
0%                35%                     65%                  100%
    ✅ SPAWN         ❌ NO SPAWN            ✅ SPAWN
```

#### **Implementation:**
```python
# Define center zone to avoid (body area)
center_zone_start = frame_width * 0.35  # 35% from left
center_zone_end = frame_width * 0.65    # 65% from left

# Randomly choose left or right side
if random.random() < 0.5:
    # Left side
    x = random.randint(MARGIN, int(center_zone_start - SIZE))
else:
    # Right side  
    x = random.randint(int(center_zone_end), width - SIZE - MARGIN)
```

#### **Benefits:**
- ✅ No body collision - only hands hit targets
- ✅ Forces player to extend arms left/right
- ✅ More realistic boxing mechanics
- ✅ Clear visual separation

---

## Technical Details:

### **Files Modified:**

#### 1. `config.py`
**Added:**
- `DODGE_DISTANCE_THRESHOLD = 80`
- `DODGE_MEMORY_DURATION = 0.3`
- `BLOCKING_DISTANCE = 100`

#### 2. `game/game_manager.py`

**Variables Added:**
```python
self.target_initial_pos = None    # Store attack target position
self.last_dodge_time = 0          # Dodge timing
self.dodge_memory_duration = 0.3  # Dodge persistence
```

**Methods Added:**
```python
def check_dodge(current_time: float) -> bool
    """Check if player dodged by moving head/body."""
```

**Methods Modified:**
- `generate_hitboxes()` - Zone-based positioning
- `update_game()` - Dodge tracking + storage
- `transition_to_enemy_attack()` - Reset dodge state
- `transition_to_player_attack()` - Reset dodge state
- `render_hud()` - Show "DODGED!" indicator
- `render_menu()` - Updated instructions

---

## Gameplay Changes:

### **Before:**
❌ Enemy attack hanya bisa di-block  
❌ Hitbox bisa spawn di tengah (body area)  
❌ Body collision = false hit  
❌ Limited defense options  

### **After:**
✅ Enemy attack bisa di-block ATAU dodge  
✅ Hitbox hanya di kiri/kanan (avoid body)  
✅ Realistic hand-only detection  
✅ 2 defense mechanics: blocking & dodging  
✅ Dynamic gameplay with movement  

---

## Testing Results:

### **Console Output Evidence:**
```
Generated 3 hitboxes (left/right only)  ✅
HIT! Hitbox at (239, 335)                ✅ Left side
HIT! Hitbox at (956, 263)                ✅ Right side
DODGED! Moved 140.2px                    ✅ Dodge detection
DODGED!                                  ✅ Dodge state active
BLOCKING!                                ✅ Block still works
BLOCKED!                                 ✅ Successful block
```

### **Dodge Testing:**
- Movement < 80px: Attack hits
- Movement > 80px: "DODGED! Moved Xpx"
- Dodge persists for 0.3 seconds after movement
- Console print throttled (0.5s interval)

### **Hitbox Testing:**
- 50% spawn on left side (x < 35%)
- 50% spawn on right side (x > 65%)
- 0% spawn in center (35% - 65%)
- No body collision detected
- All hits from hand landmarks only

---

## Visual Indicators:

### **HUD Display:**
1. **Blocking State:**
   - Text: "BLOCKING!"
   - Color: Cyan (0, 255, 255)
   - Position: Top-left (20, 100)

2. **Dodging State:**
   - Text: "DODGED!"
   - Color: Orange (255, 128, 0)
   - Position: Top-left (20, 100)

3. **Phase Instructions:**
   - Attack Phase: "PUNCH THE TARGETS!"
   - Defense Phase: "DODGE OR BLOCK!"

### **Menu Instructions Updated:**
```
ATTACK PHASE:
- Punch the targets on LEFT & RIGHT
- Hit all targets for max damage!

DEFENSE PHASE:
- Red target shows enemy attack
- BLOCK: Cover face with hands
- DODGE: Move your head/body away!
```

---

## Game Balance:

### **Dodge Parameters (Tunable):**
```python
DODGE_DISTANCE_THRESHOLD = 80  # Higher = harder to dodge
DODGE_MEMORY_DURATION = 0.3    # How long dodge state lasts
```

### **Hitbox Zone (Tunable):**
```python
center_zone_start = 0.35  # 35% - wider = less spawn area
center_zone_end = 0.65    # 65% - adjust for difficulty
```

**Recommended Settings:**
- Easy: `center_zone = 0.30-0.70` (narrow body zone)
- Medium: `center_zone = 0.35-0.65` (current)
- Hard: `center_zone = 0.40-0.60` (wide body zone, less spawn area)

---

## Performance:

- ✅ No performance impact
- ✅ Lightweight distance calculation
- ✅ Efficient zone-based spawn
- ✅ Print throttling prevents spam

---

## Future Enhancements (Optional):

- [ ] Visual trail showing dodge direction
- [ ] Dodge counter/score bonus
- [ ] Perfect dodge (last moment) = 2x bonus
- [ ] Dodge speed affects difficulty
- [ ] Different zones for different difficulties
- [ ] Combo system: dodge + block = special bonus

---

**Status**: Both features fully implemented and tested ✅

**Gameplay**: Much more dynamic and realistic! 🥊💨
