FROM elixir

ADD . /app
WORKDIR /app/

RUN mix local.hex --force
RUN mix local.rebar --force
RUN mix archive.install https://github.com/phoenixframework/archives/raw/master/phx_new.ez

RUN apt-get update
RUN apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get install -y nodejs
RUN apt-get install -y npm
RUN apt-get install -y build-essential

RUN mix do deps.get, deps.compile
RUN cd assets && npm i

CMD ["mix", "phx.server"]
