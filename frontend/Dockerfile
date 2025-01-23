FROM node:22
WORKDIR /usr/src/app

COPY package*.json ./
run npm i

COPY . .

EXPOSE 3000

ENTRYPOINT ["npm", "run"]
CMD ["start"]
