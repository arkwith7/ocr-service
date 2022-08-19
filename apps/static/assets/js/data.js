let myData = {}
let user = {}
let staticAddress = ''

const setData = (data , headings) => {
    myData = {
        data: data,
        headings: headings,
    }
}

const setUser = (u) => {
    user = u;
}

const setStaticAddress = (s) => {
    staticAddress = s
}