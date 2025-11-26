# 🎯 Impact Scoring System

## How We Score Bug Impact (0-100)

**Not all bugs are equal. Some fixes help 10 people. Others help 10,000.**

---

## The Formula

```
Impact Score = User Base (40) + Severity (30) + Ease (20) + Time (10)
```

Maximum: **100 points**

---

## Components

### 1. User Base Affected (0-40 points)

**How many people hit this bug?**

| Users Affected | Points | Example |
|----------------|--------|---------|
| All users (100%) | 40 | Core functionality broken |
| Most users (50%+) | 30 | Platform-specific (Windows, snap) |
| Many users (20-50%) | 20 | Feature-specific bug |
| Some users (<20%) | 10 | Edge case scenario |

**How to estimate:**
- Check download/install stats
- Count issue comments/reactions
- Look for duplicate reports
- Check platform usage stats

### 2. Severity (0-30 points)

**How broken is it?**

| Severity | Points | Description |
|----------|--------|-------------|
| Critical | 30 | Completely non-functional, blocks core use |
| Major | 20 | Feature broken, workaround exists |
| Moderate | 10 | Degraded experience, annoying |
| Minor | 5 | Cosmetic, low impact |

**Examples:**
- **Critical (30):** App won't install/launch
- **Major (20):** VPN won't connect
- **Moderate (10):** UI glitch, slow performance  
- **Minor (5):** Typo in help text

### 3. Fix Difficulty (0-20 points, INVERSE!)

**Easier = More Points!**

| Difficulty | Points | Time | Example |
|------------|--------|------|---------|
| Very Easy | 20 | <30 min | One-line fix, config change |
| Easy | 15 | <2 hours | Simple logic, clear solution |
| Moderate | 10 | 2-4 hours | Some refactoring needed |
| Hard | 5 | >4 hours | Major changes required |

**Why inverse?** We want high impact per hour of work!

### 4. Time to Fix (0-10 points)

| Time | Points |
|------|--------|
| < 30 minutes | 10 |
| < 2 hours | 7 |
| < 4 hours | 4 |
| > 4 hours | 2 |

**The "4-Hour Rule":** Best contributions fit in one session!

---

## Real Examples

### Example 1: WireGuard Snap Package

**Bug:** Snap package completely broken

**Scoring:**
- **User Base:** 40 pts (50,000 snap users, all affected)
- **Severity:** 30 pts (critical - won't launch)
- **Ease:** 15 pts (moderate - rebuild config)
- **Time:** 7 pts (2 hours)

**Total: 92/100** 🔥 **CRITICAL IMPACT!**

**ROI:** 2 hours → 50,000 users = 25,000 users/hour!

---

### Example 2: CSS Animation Typo

**Bug:** Missing space in CSS class

**Scoring:**
- **User Base:** 40 pts (all users see it)
- **Severity:** 5 pts (minor visual glitch)
- **Ease:** 20 pts (one-line fix)
- **Time:** 10 pts (< 30 min)

**Total: 75/100** ⭐ **HIGH IMPACT!**

**ROI:** 30 min → 50,000 users = 100,000 users/hour!

---

### Example 3: Import Dialog UX

**Bug:** Hidden files not shown in import

**Scoring:**
- **User Base:** 30 pts (affects importers)
- **Severity:** 10 pts (degraded UX)
- **Ease:** 15 pts (simple addition)
- **Time:** 10 pts (< 30 min)

**Total: 65/100** ✨ **GOOD IMPACT!**

---

## Impact Categories

### 🔥 Critical Impact (90-100)
- Affects thousands or tens of thousands
- Completely broken
- Easy to fix
- **DO THESE FIRST!**

Examples:
- Broken installation
- Won't launch on major platform
- Security vulnerability
- Data loss bugs

### ⭐ High Impact (70-89)
- Affects many users
- Major functionality issues OR easy fixes
- Worth your time!

Examples:
- Feature not working
- Performance problems
- Easy fixes with wide reach

### ✨ Good Impact (50-69)
- Moderate user base OR moderate severity
- Still worth fixing
- Good for learning

Examples:
- Platform-specific issues
- Edge case bugs
- UX improvements

### 🤷 Low Impact (0-49)
- Few users affected
- Minor issues
- Hard to fix
- **Skip unless passionate about it**

Examples:
- Typos in comments
- Rare edge cases
- Cosmetic issues needing major work

---

## Using Impact Scores

### For Contributors

**Ask yourself:**
> "Is this the best use of my 4 hours?"

```
Bug A: Score 45 (typo in docs)
Bug B: Score 92 (broken for 50,000 users)

→ Fix Bug B! 2x the score = way more impact!
```

### For "Impact Saturdays"

**Target: 70+ score**

Why? High impact per hour invested:
- Meaningful contribution
- Helps thousands
- Feels rewarding
- Builds momentum

### For First Contributions

**Sweet spot: 60-80 score**

- High enough to matter
- Easy enough to complete
- Builds confidence
- Good learning experience

---

## Advanced: Calculating Your ROI

**Return on Investment = Users Helped / Hours Spent**

### Example Calculations

**WireGuard Snap (92 pts):**
```
50,000 users / 2 hours = 25,000 users/hour
ROI: 25,000:1 🔥
```

**CSS Fix (75 pts):**
```
50,000 users / 0.5 hours = 100,000 users/hour
ROI: 100,000:1 🔥🔥🔥
```

**Random Typo (20 pts):**
```
100 users / 0.1 hours = 1,000 users/hour
ROI: 1,000:1 😐
```

**See the difference?** High-impact bugs have 25-100x better ROI!

---

## The Tool Does This For You

```bash
ansai-pr-discover --high-impact

# Output automatically scored:
🔥 Score: 92 | Broken snap package
   Users: ~50,000
   Severity: Critical
   Time: ~2 hours
   ROI: 25,000 users/hour
   → THIS IS CRITICAL IMPACT! Fix this!

⭐ Score: 75 | CSS animation bug
   Users: ~50,000
   Severity: Minor
   Time: ~30 min
   ROI: 100,000 users/hour
   → Quick win with huge reach!

🤷 Score: 35 | Typo in code comment
   Users: ~50
   Severity: Minor
   Time: ~5 min
   ROI: 600 users/hour
   → Skip this, low impact
```

---

## Impact Mindset

### Old Way
> "I'll fix this typo because it's easy"

**Result:** 10 minutes, 5 people helped

### New Way (Impact-Driven)
> "What bug affects the MOST people that I can fix?"

**Result:** 2 hours, 50,000 people helped

**That's 10,000x more impact for 12x more time!**

---

## Remember

**Your time is valuable.**  
**Other people's time is valuable.**  
**Fix bugs that save the most time for the most people.**

**That's impact-driven contribution!** 🎯

