'use strict'

const User = use('App/Models/User')

class UserController {
    async list ({ request, response}) {
        let users = await User.all()

        return response.json(users)
    }
}

module.exports = UserController