document.addEventListener('DOMContentLoaded', ()=>load_posts());
document.addEventListener('DOMContentLoaded', ()=>create_post());
document.addEventListener('DOMContentLoaded', ()=>load_profile());
document.addEventListener('DOMContentLoaded', ()=>load_following_page());


//getting csrf token 
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//csrf token value
const csrf_token = getCookie('csrftoken');

//FUNCTIONS FOR INDEX PAGE START
//this function returns post card html for given data
function create_post_card(post){
    const card_wrapper = document.createElement('div');
    card_wrapper.className = 'card border border-info rounded mb-4 p-3';
    card_wrapper.append(post_content_display(post, card_wrapper));
    return card_wrapper;
}


//this function returns inner HTML element for card_wrapper
function post_content_display(post, card_wrapper){
    const card_body = document.createElement('div');
    card_body.className = 'card_body';
    card_wrapper.append(card_body);
    //adding title
    const card_title_wrapper= document.createElement('h5');
    card_title_wrapper.className = 'card-title mb-2';
    const icon = document.createElement('i');
    icon.className = 'fa-solid fa-user';
    const profile_link = document.createElement('a');
    profile_link.href = `/profile/user=${post.creator}`
    profile_link.className = 'mx-3 profile_link';
    profile_link.innerText = post.creator;
    card_title_wrapper.append(icon);
    card_title_wrapper.append(profile_link);
    card_body.append(card_title_wrapper);
    //adding creation date
    const creation_date = document.createElement('h6');
    creation_date.className = 'card-title mb-2';
    creation_date.innerText = post.creation_date;
    if(post.edited){
        //let the user know if the post has been edited
        creation_date.innerText+=' (edited)';
    }
    card_body.append(creation_date);
    //adding text content
    const text_content = document.createElement('p');
    text_content.className = 'card-text';
    text_content.innerText = post.text_content;
    card_body.append(text_content);
    //adding edit
    if(post.editing_allowed){
        const edit = document.createElement('button');
        edit.id = 'edit_button';
        edit.innerText = 'Edit';
        edit.addEventListener('click', (event)=>{
            card_wrapper.innerHTML = '';
            let edit_form = create_edit_form(post,card_wrapper);
            card_wrapper.append(edit_form);
        });
        card_body.append(edit);
    }
    //creating like button
    const like_button_wrapper = document.createElement('span');
    create_like_button(like_button_wrapper, post);
    card_body.append(like_button_wrapper);

    return card_body;
}


function create_edit_form(post, card_wrapper){
    //change inner html of the post
    //create text are with current post`s text_content
    let edit_form = document.createElement('div');
    let edit_textarea = document.createElement('textarea');
    edit_textarea.className = 'form-control border border-info rounded mb-2';
    edit_textarea.id = 'edit_post_textarea';
    edit_textarea.rows = 3;
    edit_textarea.innerText = post.text_content;
    edit_form.append(edit_textarea);
    //create save button for changes
    let save_button = document.createElement('button');
    save_button.className='btn btn-primary rounded my-2';
    save_button.innerText = 'Save';
    //adding functionality to the save button
    save_button.addEventListener('click',()=>{
        const new_text_content = edit_textarea.value;
        console.log(new_text_content, typeof(new_text_content));
        if(new_text_content.length>0){
            //if textarea is not empty
            fetch(`/edit_post/${post.id}`,{
                method:'PUT',
                headers:{
                    'Content-Type':'application/json',
                    'X-CSRFToken':csrf_token
                },
                body:JSON.stringify({
                    'updated_text_content': new_text_content
                })
            })
            .then(response => response.json())
            .then(updated_post_content =>{
                console.log(updated_post_content);
                card_wrapper.innerHTML = '';
                card_wrapper.append(post_content_display(updated_post_content, card_wrapper));
            })
        }
    });
    edit_form.append(save_button);
    return edit_form;
}

function create_like_button(like_button_wrapper, post){
    //heart shaped like button
    like_button_wrapper.innerHTML = '';
    const like_button = document.createElement('button');
    like_button.id  = 'like_button';
    const like_icon = document.createElement('i');
    like_icon.className = 'fa-solid fa-heart';
    like_button.append(like_icon);
    like_button_wrapper.append(like_button);
    //like count
    const like_count = document.createElement('span');
    like_count.id  = 'like_count';
    like_count.innerText = post.like_count;
    like_button_wrapper.append(like_count);
    if(post.liked_by_user){
        like_button.style.color = '#D2042D';
        like_button.addEventListener('click', ()=>like_unlike_post(like_button_wrapper, post, method = 'DELETE'));
    }else{
        like_button.style.color = 'white';
        like_button.addEventListener('click', ()=>like_unlike_post(like_button_wrapper, post, method = 'POST'));    
    }
}


function like_unlike_post(like_button_wrapper, post, method){
    fetch('/like_unlike_post',{
        method:method,
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrf_token
        },
        body:JSON.stringify({
            "post_id":post.id
        })
    })
    .then(response => response.json())
    .then(updated_post => {
        //update like count
        create_like_button(like_button_wrapper, updated_post);
    })
}


//this function fetches posts from the requested url and displays them with pagination
function create_pagination(container,url){
    container.innerHTML='';
    //fetch posts from url
    fetch(url)
    .then(response => response.json())
    .then (posts => {
        console.log(posts)
        if(posts.results.length>0){
            //add posts to the container
            for(i in posts.results){
                let new_post = create_post_card(posts.results[i]);
                container.append(new_post);
            }
            //add pagination buttons to the page
            const pagination_wrapper = document.getElementById('pagination-wrapper');
            if(pagination_wrapper){
                pagination_wrapper.innerHTML='';
                //add previous button
                let previous_button_parent = document.createElement('li');
                previous_button_parent.className = 'page-item';
                let previous_button = document.createElement('button');
                previous_button.className = 'page-link border border-info rounded-pill text-center';
                previous_button.id = 'pagination-previous';
                previous_button.innerText = 'Previous';
                //add functionality to the previous button
                if(posts.previous===null){
                    previous_button.disabled = true;
                }else{
                    previous_button.addEventListener('click',()=>create_pagination(container,posts.previous))
                }
                previous_button_parent.append(previous_button);
                pagination_wrapper.append(previous_button_parent);
                //add next button
                let next_button_parent = document.createElement('li');
                next_button_parent.className = 'page-item';
                let next_button = document.createElement('button');
                next_button.className = 'page-link border border-info rounded-pill mx-3 text-center';
                next_button.id = 'pagination-next';
                next_button.innerText = 'Next';
                //add functionality to the next button
                if(posts.next===null){
                    next_button.disabled = true;
                }else{
                    next_button.addEventListener('click',()=>create_pagination(container,posts.next))
                }
                next_button_parent.append(next_button);
                pagination_wrapper.append(next_button_parent);
            }
            
        }
    })
}

//this function loads posts on All Posts page.
function load_posts(){
    const post_wrapper = document.querySelector('#all_posts_wrapper');
    // fetching posts from our django-rest API
    if(post_wrapper){
        const url = '/all_posts'
        //load posts with pagination
        create_pagination(post_wrapper,url);
    }
}


//this function sends POST request to django-rest API to create a new post
function create_post(){
    const form = document.querySelector('#create_post_form');
    if(form){
        form.addEventListener('submit',(e)=>{
            e.preventDefault();
            const text_content = document.getElementById('create_post_textarea').value;
            //const csrf_token = document.querySelector("form[name=create_post_form] input[name=csrfmiddlewaretoken").value;
            console.log(text_content, text_content.length);
            console.log(typeof(text_content));
            if(text_content.length > 0){
                fetch('/create_post',{
                    method:'POST',
                    headers:{
                        'Content-Type':'application/json',
                        'X-CSRFToken':csrf_token
                    },
                    body:JSON.stringify({
                        'text_content': text_content
                    })
                })
                .then(response => response.json())
                .then(post=>{
                    document.getElementById('create_post_form').reset();
                    const post_wrapper = document.querySelector('#all_posts_wrapper');
                    post_wrapper.prepend(create_post_card(post));
                })
                .catch(error => console.log(error))
            }
        })
    }
}
//FUNCTIONS FOR INDEX PAGE END

//PROFILE PAGE FUNCTIONS START
//functions below take care of displaying user`s data on their profile page
function load_profile(){
    let profile_info_wrapper = document.getElementById('profile_info_wrapper');
    if(profile_info_wrapper){
        let url = window.location.href;
        let username = url.split('=')[1];
        //console.log(username, typeof(username), username.length);
        load_profile_data(username);
        load_profile_posts(username);
    }
}

function load_profile_data(username){
    //fetch profile data
    let profile_username = document.getElementById('profile_username');
    let following_count = document.getElementById('profile_following_count');
    let followers_count = document.getElementById('profile_followers_count');
    let following_button_wrapper = document.getElementById('profile_following_button_wrapper');
    fetch(`/user_profile_info/${username}`)
    .then(response => response.json())
    .then(data => {
        profile_username.innerText = data.username;
        following_count.innerText = data.following;
        followers_count.innerText = data.followers;
        if(following_button_wrapper){
            //if user is not on their page
            following_button_wrapper.innerHTML='';
            if(data.is_following){
                following_button_wrapper.append(unfollow_form(data));
                //document.getElementById('unfollow_form').addEventListener('submit',(e)=>unfollow(e));
            }else{
                following_button_wrapper.append(follow_form(data));
            }
        }
    })
}

function unfollow_form(user){
    //create unfollow form
    const unfollow_form = document.createElement('form');
    unfollow_form.id = 'unfollow_form';
    const unfollow_button = document.createElement('input');
    unfollow_button.type= 'submit'; 
    unfollow_button.className = 'btn btn-danger rounded';
    unfollow_button.id = 'unfollow_button';
    unfollow_button.value = 'Unfollow';
    unfollow_form.append(unfollow_button);
    //setting Followed object as deleted in db
    unfollow_form.addEventListener('submit',(e)=>{
        e.preventDefault();
        fetch('/unfollow',{
            method:'PUT',
            headers:{
                'Content-Type':'application/json',
                'X-CSRFToken':csrf_token
            },
            body:JSON.stringify({
                'followers': user.username
            })
        })
        .then(response => response.json())
        .then(data =>{
            load_profile_data(user.username);
        })
    });
    return unfollow_form;
}

function follow_form(user){
    //creating follow form
    const follow_form = document.createElement('form');
    follow_form.id = 'follow_form';
    const follow_button = document.createElement('input');
    follow_button.type= 'submit'; 
    follow_button.className = 'btn btn-primary rounded';
    follow_button.id = 'follow_button';
    follow_button.value = 'Follow';
    follow_form.append(follow_button);
    //creating Followed object in db with fetch and re-fetching profile page data on submit
    follow_form.addEventListener('submit',(e)=>{
        e.preventDefault();
        fetch('/follow',{
            method:'POST',
            headers:{
                'Content-Type':'application/json',
                'X-CSRFToken':csrf_token
            },
            body:JSON.stringify({
                'followers': user.username
            })
        })
        .then(response => response.json())
        .then(data =>{
            load_profile_data(user.username);
        })
    });
    return follow_form;
}

function load_profile_posts(profile_username){
    //fetch user`s posts
    let profile_posts_wrapper = document.getElementById('profile_page_posts_wrapper');
    if(profile_posts_wrapper){
        let url = `/profile_posts/${profile_username}`;
        create_pagination(profile_posts_wrapper,url);
    }
}

//PROFILE PAGE FUNCTIONS END

//FUNCTIONS FOR FOLLOWING PAGE START
function load_following_page(){
    const following_page_wrapper = document.getElementById('following_page_wrapper');
    if(following_page_wrapper){
        const following_page_posts = document.getElementById('following_page_posts');
        let url = `/following_posts`;
        create_pagination(following_page_posts,url);
    }
}

//FINCTIONS FOR FOLLOWING PAGE END



