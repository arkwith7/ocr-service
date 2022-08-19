
const formConstructor = (item) => {
    // create form
    const form = document.getElementById('form')
    form.className = 'd-flex flex-wrap gap-2 p-4'
    form.innerHTML = ''

    const avatarContainer = document.createElement('div')
    avatarContainer.className = 'd-flex flex-column gap-1'

    const avatarImg = document.createElement('img')
    avatarImg.setAttribute('src',item[0].image ? item[0].image : `${staticAddress}/images/user/avatar-5.jpg`);
    avatarImg.className = 'img-radius img-fluid wid-80'
    avatarImg.id = 'avatar-img'

    const avatarInput = document.createElement('input')
    avatarInput.setAttribute('type','file')
    avatarInput.className = ''
    avatarInput.setAttribute('accept','accept="image/*')
    avatarInput.name = 'avatar'
    avatarInput.id = 'avatar-input'

    avatarContainer.appendChild(avatarImg)
    avatarContainer.appendChild(avatarInput)

    form.innerHTML += avatarContainer.outerHTML

    for (let i in item[0]) {

        if (i !== 'image' && i !== 'registration_date' && i !== 'status') {

            const inputContainer = document.createElement('div')
            inputContainer.className = (i === 'address' ? 'flex-grow-1' : '')

            const label = document.createElement('label')
            label.setAttribute('htmlFor', i)
            label.innerHTML = i[0].toUpperCase() + i.slice(1,i.length);
            label.className = "form-label m-0";

            const input = document.createElement('input');
            input.setAttribute('type', 'text');
            input.className = 'form-control m-0'
            input.name = i

            if (i === 'email')
                input.setAttribute('readonly', 'true')

            if (i === 'username')
                inputContainer.setAttribute('hidden', 'true')

            input.setAttribute('value', item[0][i])

            inputContainer.appendChild(label)
            inputContainer.appendChild(input)

            form.innerHTML += inputContainer.outerHTML
        }
    }

    document.getElementById('avatar-input').onchange = (e) => {
        document.getElementById('avatar-img').setAttribute('src', URL.createObjectURL(e.target.files[0]))
    }

    return form;
}