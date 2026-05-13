// Basic Interactivity for Issue Reporter

document.addEventListener('DOMContentLoaded', () => {
    // Voting logic
    const voteButtons = document.querySelectorAll('.vote-btn');
    
    voteButtons.forEach(btn => {
        btn.addEventListener('click', async () => {
            const issueId = btn.dataset.issueId;
            
            // Toggle class for visual feedback
            btn.classList.toggle('voted');
            const countSpan = btn.querySelector('.vote-count');
            let currentCount = parseInt(countSpan.textContent);
            
            if (btn.classList.contains('voted')) {
                currentCount++;
            } else {
                currentCount--;
            }
            
            countSpan.textContent = currentCount;
            
            // In a real app, we would send this to the server
            try {
                const response = await fetch(`/vote/${issueId}`, { method: 'POST' });
                if (response.status === 401) {
                    const data = await response.json();
                    window.location.href = data.redirect;
                    return;
                }
                const data = await response.json();
                countSpan.textContent = data.new_vote_count;
            } catch (err) {
                console.error('Error voting:', err);
                // Revert visual toggle if there was an error
                btn.classList.toggle('voted');
            }
        });
    });

    // Handle filter chips
    const filterChips = document.querySelectorAll('.filter-chip');
    filterChips.forEach(chip => {
        chip.addEventListener('click', () => {
            filterChips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            
            // Logic to filter the grid
            const selectedCategory = chip.textContent.trim();
            const issueCards = document.querySelectorAll('.issue-card');
            
            // In a more complex app, we might re-fetch or filter DOM
            issueCards.forEach(card => {
                const category = card.dataset.category;
                if (selectedCategory === 'All' || category === selectedCategory) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
});
