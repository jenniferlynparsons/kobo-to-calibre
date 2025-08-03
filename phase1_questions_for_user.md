# Phase 1: User Configuration Questions

Based on the analysis of your Kobo database and Calibre library samples, please answer these questions to guide the sync tool development.

## Collection and Rating System Questions

### Q1: Rating System
Your Kobo database doesn't show traditional star-rating collections (like "1-star", "2-star", etc.). How do you currently rate books?

- [ ] I don't rate books, just categorize them
- [ ] I use the Kobo favorites system (heart icon)
- [X] I have specific collection names that represent ratings (please specify which ones)
  
- [ ] I rate books in Calibre directly, not on Kobo
- [ ] Other: _______________

**If you use collections for ratings, please list them:**
- Collection name → Rating value
- Example: "loved it" → 5 stars
- Evergreen - 5 stars
- Absolute Favorite - 4 stars
- Favorites - 3 stars
- Great - 2 stars (Great in Calibre == Good on Kobo)

### Q2: Collection Priorities
Your Kobo has 30 active collections. Which ones should the sync tool prioritize?

**Collections found in your database:**
- "new jersey", "mix", "sweet fluff", "fix", "kink", "> no band", "killjoys", "historic au", "little", "sickfic"
- Plus 20 others

**Sync preferences:**
- [x] Sync ALL collections to Calibre as categories in custom columns
- [ ] Sync only genre/content collections, ignore location-based ones
- [ ] Only sync these specific collections: _______________
- [ ] Group collections by type (content warning vs genre vs fandom)

### Q3: Collection Handling for Books in Multiple Categories
How should books that appear in multiple Kobo collections be handled in Calibre?

- [ ] Combine all collections as comma-separated tags (e.g., "sweet fluff, killjoys, historic au")
- [ ] Use primary/most important collection only
- [ ] Create separate custom columns for different collection types
- [ ] Use Calibre's existing tag system as-is
- [x] Other approach: I use categories in custom columns (My Ratings, My Genres)

## Library Structure Questions

### Q4: Calibre Library Mapping
You have multiple Calibre libraries. How should collections be synced differently for each?

**MCR Library Sample** (appears to be My Chemical Romance fanfiction):
- [x] Full metadata sync (all collections, reading status, dates)
- [ ] Genre/content collections only
- [ ] Minimal sync (just read/unread status)
- [ ] Custom mapping: _______________

**Misc Library Sample** (appears to be other fandoms/published works):
- [x] Same as MCR library
- [ ] Different approach: _______________
- [ ] Skip this library entirely

**Other Calibre libraries** (if any):
Please list any other Calibre libraries and desired sync behavior: I have multiple libraries with similar structures to the Misc library. I would like to use that library structure for all of them. There are a few libraries that have less metadata, so there may be a need to handle missing metadata without erroring.

### Q5: Metadata Granularity
How detailed should the metadata sync be for each library type?

**For fanfiction libraries (like MCR):**
- [x] Full sync: collections, reading status, reading dates, progress
- [ ] Medium sync: collections and reading status only
- [ ] Light sync: just mark as read/unread

**For published works libraries:**
- [x] Same as fanfiction
- [ ] Different: _______________

## Technical Preferences

### Q6: Book Matching Strategy
How should the tool match books between Kobo and Calibre when titles don't match exactly?

- [ ] Automatic matching with manual review of uncertain matches
- [x] Strict title+author matching only (skip uncertain matches) - this should also make a list of anything that was skipped for review
- [ ] Fuzzy matching with confidence scoring
- [ ] Always prompt for manual confirmation
- [ ] Other: _______________

### Q7: Conflict Resolution
What should happen when Kobo data conflicts with existing Calibre metadata?

**Scenario: Book has rating in Calibre but different status in Kobo**
- [ ] Kobo data takes precedence (overwrite Calibre)
- [ ] Calibre data takes precedence (skip Kobo updates)
- [x] Prompt for manual decision
- [ ] Create backup of original Calibre data
- [ ] Merge data when possible

### Q8: Safety and Backup Preferences
How cautious should the tool be with your Calibre libraries?

- [ ] Always create full backup before any changes
- [ ] Create backup only on first run
- [x] Just backup metadata.db file
- [ ] No automatic backups (I'll handle this myself)
- [ ] Other: _______________

**Dry-run preference:**
- [ ] Always show preview of changes before applying
- [ ] Only for first few runs
- [ ] Skip dry-run, just do it
- [ ] Make dry-run the default mode
- [x] can we make dry run optional?

## Workflow Questions

### Q9: Sync Frequency and Trigger
How often and when should sync happen?

**Frequency:**
- [ ] After every reading session
- [ ] Daily automatic sync
- [ ] Weekly batch sync
- [x] Manual trigger only
- [ ] When Kobo is connected to computer

**Trigger method:**
- [ ] Command line script I run manually
- [x] GUI application with sync button
- [ ] Automatic when Kobo device detected
- [ ] Scheduled task/cron job
- [ ] Calibre plugin integration

### Q10: Progress Reporting and Logging
How much detail do you want about what the sync tool does?

**Logging level:**
- [ ] Minimal: just success/failure summary
- [ ] Medium: list of books updated and changes made
- [x] Verbose: detailed progress and debug information
- [ ] Custom: specify what information is important to you

**Output format:**
- [ ] Terminal/console output only
- [ ] Log file saved for review
- [x] Both console and log file
- [x] GUI progress dialog

## Future Features

### Q11: Advanced Features
Which future enhancements would be most valuable?

**Priority ranking (1-5, 1 = most important):**
- [5] Reading time tracking and estimates
- [5] Sync reading notes/annotations  
- [5] Two-way sync (Calibre changes back to Kobo)
- [5] Multiple Kobo device support
- [5] Integration with other e-readers
- [3] Web interface for configuration
- [5] Sharing sync configurations with other users

### Q12: Plugin vs Standalone
What's your preferred final form for this tool?

- [x] Calibre plugin (integrated into Calibre interface)
- [ ] Standalone script (run from command line)
- [x] GUI application (separate from Calibre)
- [ ] Both plugin and standalone versions
- [ ] Web service/cloud-based solution

---

## Additional Comments

Please add any other requirements, concerns, or preferences not covered above:

I would like to focus on the gui application first and only try creating a Calibre plugin when we're sure it's working as expected.

---

**Next Steps After Completing This Survey:**
1. Review your responses and clarify any unclear answers
2. Begin Phase 2 development with your specific requirements
3. Create initial proof-of-concept script based on your preferences
4. Test with small subset of your library before full implementation