document.addEventListener('DOMContentLoaded', function() {
    //gets all the hidden projects and the show more button
    const hiddenProjects = document.querySelectorAll('.hidden-project');
    const showMoreBtn = document.getElementById('show-more-btn');

    // if there's no button or no hidden projects, exit early
    if (!showMoreBtn || hiddenProjects.length === 0) return;


    let projectsToShow = 3; // Show 3 more projects at a time
    let projectsShown = 0;


    showMoreBtn.addEventListener('click', function() {

        const nextBatch = Array.from(hiddenProjects).slice(
            projectsShown,
            projectsShown + projectsToShow
        );


        nextBatch.forEach((project, index) => {
            setTimeout(() => {

                project.classList.remove('hidden-project');
                project.classList.add('fade-in');


                project.style.animationDelay = `${index * 0.1}s`;
            }, index * 100);
        });


        projectsShown += nextBatch.length;


        updateButtonState();
    });


    function updateButtonState() {
        const remainingProjects = hiddenProjects.length - projectsShown;


        if (remainingProjects <= 0) {
            showMoreBtn.style.display = 'none';
            return;
        }


        const countSpan = showMoreBtn.querySelector('.remaining-count');
        if (countSpan) {
            countSpan.textContent = `(${remainingProjects} more)`;
        }


        if (remainingProjects < projectsToShow) {
            showMoreBtn.querySelector('.btn-text').textContent = 'Show All Projects';
        }
    }
});