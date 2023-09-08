local function get_user()
    local id = math.random(0, 500)
    local user_name = "Cornell_" .. tostring(id)
    local pass_word = ""
    for i = 0, 9, 1 do 
      pass_word = pass_word .. tostring(id)
    end
    return user_name, pass_word
  end


request = function()
    wrk.headers["Connection"] = "Keep-Alive"
    local user_name, password = get_user()
    local path = "/user?username=" .. user_name .. "&password=" .. password
    return wrk.format("GET", path)
  end