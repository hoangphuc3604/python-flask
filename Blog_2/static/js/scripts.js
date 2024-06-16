/*!
* Start Bootstrap - Clean Blog v6.0.9 (https://startbootstrap.com/theme/clean-blog)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-clean-blog/blob/master/LICENSE)
*/
window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0;
    const mainNav = document.getElementById('mainNav');
    const headerHeight = mainNav.clientHeight;
    window.addEventListener('scroll', function() {
        const currentTop = document.body.getBoundingClientRect().top * -1;
        if ( currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove(['is-visible']);
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop;
    });
})

follow_btn = document.getElementById('follow-btn-profile')
fl = follow_btn.classList[follow_btn.classList.length - 2].split('-')
followed = fl[0]
follower = fl[1]

follow_btn.addEventListener('click', () => {
    if (follow_btn.classList[follow_btn.classList.length - 1] == 'not-fl') {
        if (follower == followed) {
            alert('You cannot follow yourself !!')
            return
        }

        follow_btn.classList.remove('not-fl')
        follow_btn.classList.add('fl')
        follow_btn.innerHTML = 'Unfollow'
        fetch('/follow', {
            method: 'POST',
            body: JSON.stringify({
                'follower': follower,
                'followed': followed
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
    } else {
        follow_btn.classList.remove('fl')
        follow_btn.classList.add('not-fl')
        follow_btn.innerHTML = 'Follow'
        fetch('/unfollow', {
            method: 'POST',
            body: JSON.stringify({
                'follower': follower,
                'followed': followed
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
    }
})