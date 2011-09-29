# -*- coding: utf-8 -*-
require 'sinatra'
require 'haml'
require 'sass'
require 'coffee-script'
require 'redis'

$redis = Redis.new

set :port, 8182
set :environment, :production

not_found do
  @title = "404"
  myhaml :not_found
end

error do
  @title = "error.."
  myhaml :error
end

get '/' do
  myhaml :index 
end

post '/press' do
  "#{$redis.incr 'press_button_number'}"
end

def myhaml target, args={}
  args.merge! :layout => false if params[:_pjax]
  haml target, args
end

def link_to name, link, pjax=""
  pjax = "class=\"js-pjax\"" unless pjax == ""
  "<a href=\"#{link}\"#{pjax}>#{name}</a>"
end

get '/main.css' do
  sass :main
end

get '/main.js' do
  coffee :main
end
