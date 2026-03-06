description = [[
#!/usr/bin/python3
# @Мартин.
# ███████╗              ██╗  ██╗    ██╗  ██╗     ██████╗    ██╗  ██╗     ██╗    ██████╗
# ██╔════╝              ██║  ██║    ██║  ██║    ██╔════╝    ██║ ██╔╝    ███║    ╚════██╗
# ███████╗    █████╗    ███████║    ███████║    ██║         █████╔╝     ╚██║     █████╔╝
# ╚════██║    ╚════╝    ██╔══██║    ╚════██║    ██║         ██╔═██╗      ██║     ╚═══██╗
# ███████║              ██║  ██║         ██║    ╚██████╗    ██║  ██╗     ██║    ██████╔╝
# ╚══════╝              ╚═╝  ╚═╝         ╚═╝     ╚═════╝    ╚═╝  ╚═╝     ╚═╝    ╚═════╝
]]

author = "Maptnh"
categories = {"vuln"}

local stdnse = require "stdnse"
local shortport = require "shortport"
local comm = require "comm"
local base64 = require "base64"
local re = require "re"
local os = require "os" 
 
local is_terminal = false
 
local ok, res = pcall(function() return io.stdout:isatty() end)
if ok then
  is_terminal = res
else
  is_terminal = false
end


local RED   = is_terminal and "\27[31m" or ""
local GREEN = is_terminal and "\27[32m" or ""
local YELLOW= is_terminal and "\27[33m" or ""
local RESET = is_terminal and "\27[0m" or ""
 
local USER = "admin"
local PASSWORD = "123456"
local BASIC_AUTH = base64.enc(USER .. ":" .. PASSWORD)
local UA_LIST = {
  "LIVE555 Streaming Media v20210827",
  "VLC/3.0.18 LibVLC/3.0.18",
  "FFmpeg/5.1.2",
  "Darwin/20.6.0 (libavformat/58.76.100)"
}
local CHECK_PATHS = {
  "/Streaming/Channels/101", "/live", "/0", "/1", "/11", "/12", "/live.sdp",
  "/Streaming/Channels/102", "/Streaming/Channels/1", "/Streaming/Channels/1601",
  "/cam/realmonitor?channel=1&subtype=0", "/cam/realmonitor?channel=1&subtype=1",
  "/cam/realmonitor", "/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=onvif",
  "/axis-media/media.amp", "/axis-cgi/mjpg/video.cgi", "/axis-cgi/media.cgi",
  "/SNC/media/media.amp", "/stream1", "/stream2", "/videoMain", "/videoSub",
  "/h264", "/h265", "/ch0_0.h264", "/ch1_0.h264", "/live/ch00_0", "/live/ch0",
  "/live/channel1", "/live/channel0", "/ipcam.sdp", "/cam1/h264", "/video-stream",
  "/h264_stream", "/live_mpeg4.sdp", "/media/video1", "/media/video2",
  "/unicast/c1/s0/live", "/unicast/c2/s1/live", "/ucast/1/1",
  "/live/video/profile1", "/live/video/profile2", "/live/h264", "/live/mpeg4",
  "/live/h264_ulaw/VGA", "/live/h264_ulaw/HD720P", "/live/h264/HD1080",
  "/live/h264/HD1080P", "/mpeg4/media.amp?resolution=640x480"
}
 
prerule = function()
  io.write([[
    ____  __                __      ______      __       _   __                    
   / __ )/ /___  ____  ____/ /     / ____/___ _/ /_     / | / /___ ___  ____ _____ 
  / __  / / __ \/ __ \/ __  /_____/ /   / __ `/ __/    /  |/ / __ `__ \/ __ `/ __ \
 / /_/ / / /_/ / /_/ / /_/ /_____/ /___/ /_/ / /_     / /|  / / / / / / /_/ / /_/ /
/_____/_/\____/\____/\__,_/      \____/\__,_/\__/____/_/ |_/_/ /_/ /_/\__,_/ .___/ 
                                               /_____/                    /_/      
Maptnh@S-H4CK13              Cameras Scan script for Nmap        https://github.com/MartinxMax  
============================================================================================================
]])   
  return false
end

 
math.randomseed(os.time())

 
local function random_ua()
  return UA_LIST[math.random(#UA_LIST)]
end
 
local function extract_server_banner(resp)
  if not resp then return "N/A" end
  local banner = resp:match("[Ss]erver:%s*(.-)\r?\n")
  if banner and #banner > 0 then return banner end
  return "N/A"
end

 
local function is_rtsp_service(host, port)
  local banner = ""
  if port.version and port.version.product then
    banner = banner .. port.version.product .. " "
  end
  if port.version and port.version.version then
    banner = banner .. port.version.version .. " "
  end
  if port.version and port.version.extrainfo then
    banner = banner .. port.version.extrainfo .. " "
  end
  if port.service then
    banner = banner .. port.service .. " "
  end

 
  if banner:lower():find("rtsp") ~= nil then
    return true
  end

 
  local ua = random_ua()
  local options_req = string.format(
    "OPTIONS rtsp://%s:%d/ RTSP/1.0\r\nCSeq: 1\r\nUser-Agent: %s\r\n\r\n",
    host.ip, port.number, ua
  )

  local ok, resp = comm.exchange(host, port, options_req, {timeout = 3000, connect_timeout = 3000})
  if not ok then
    return false
  end

  if resp and resp:lower():find("rtsp") then
    return true
  end

  return false
end

 
local function rtsp_options(host, port)
  local ua = random_ua()
  local options_req = string.format(
    "OPTIONS rtsp://%s:%d/ RTSP/1.0\r\nCSeq: 1\r\nUser-Agent: %s\r\n\r\n",
    host.ip, port.number, ua
  )

  local ok, resp = comm.exchange(host, port, options_req, {timeout = 5000})
  if not ok then
    return nil, "OPTIONS connection/receive failed: " .. (resp or "unknown error")
  end

  local server_banner = extract_server_banner(resp)
  return server_banner, nil
end
 
local function rtsp_describe(host, port, path)
  local ua = random_ua()
  local auth_hdr = string.format("Authorization: Basic %s\r\n", BASIC_AUTH)
  local describe_req = string.format(
    "DESCRIBE rtsp://%s:%d%s RTSP/1.0\r\nCSeq: 3\r\nAccept: application/sdp\r\nUser-Agent: %s\r\n%s\r\n",
    host.ip, port.number, path, ua, auth_hdr
  )

  local ok, resp = comm.exchange(host, port, describe_req, {timeout = 5000})
  if not ok then
    return nil, "DESCRIBE connection/receive failed: " .. tostring(resp)
  end

 
  local status_code = resp:match("RTSP/1%.0%s+(%d+)")
  if not status_code then
    return nil, "Failed to extract RTSP status code"
  end

  return tonumber(status_code), nil, resp
end

 
portrule = function(host, port)
  return port.state == "open" and is_rtsp_service(host, port)
end

 
action = function(host, port)
  local result = {}
  local target_port = port.number

 
  local server_banner, banner_err = rtsp_options(host, port)
  if banner_err then
    server_banner = "N/A"
  end

 
  local anon_paths = {}
  local auth_paths = {}

  for _, path in ipairs(CHECK_PATHS) do
    local status_code, desc_err, raw = rtsp_describe(host, port, path)
    if desc_err then
 
    else
      if status_code == 200 then
        table.insert(anon_paths, path)
      elseif status_code == 401 then
        table.insert(auth_paths, path)
      end
    end
  end
 
    if #anon_paths > 0 then
    table.insert(result, string.format("    [%sBlood-Cat Anonymous Login%s] [%s:%s]",RED,RESET,USER,PASSWORD))
    table.insert(result, string.format("    [*] %s%s:%d%s - Server Banner: %s", RED,host.ip, target_port,RESET, server_banner))
    for _, p in ipairs(anon_paths) do
        table.insert(result, string.format("            |  %s%s%s", RED,p,RESET))
    end
  elseif #auth_paths > 0 then
    table.insert(result, string.format("    [%sBlood-Cat Requires credentials%s]",YELLOW,RESET))
    table.insert(result, string.format("    [*] %s%s:%d%s - Server Banner: %s", YELLOW,host.ip, target_port,RESET, server_banner))
    for _, p in ipairs(auth_paths) do
      table.insert(result, string.format("            |  %s%s%s", YELLOW,p,RESET))
    end
  else
    table.insert(result, string.format("    [?] %s:%d - No valid paths detected", host.ip, target_port))
  end
  table.insert(result, "  ")
 
 
   return stdnse.format_output(true, result)  
end

 