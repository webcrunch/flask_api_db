USE auctionista;

CREATE TABLE
    `items`(
        `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `title` VARCHAR(255) NOT NULL,
        `short_text` VARCHAR(255) NOT NULL,
        `description` VARCHAR(2550) NOT NULL,
        `start_time` DATETIME NOT NULL,
        `termination_time` DATETIME NOT NULL,
        `starting_price` INT NOT NULL,
        `category` VARCHAR(255) NOT NULL,
        `user` INT UNSIGNED NOT NULL
    );

CREATE TABLE
    `users`(
        `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `email` VARCHAR(255) NOT NULL,
        `password` VARCHAR(255) NOT NULL,
        `username` VARCHAR(255) NOT NULL
    );

CREATE TABLE
    `images`(
        `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `name` VARCHAR(255) NOT NULL,
        `url` VARCHAR(255) NOT NULL,
        `auction_object` INT UNSIGNED NOT NULL
    );

CREATE TABLE
    `bids`(
        `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
        `amount` BIGINT NOT NULL,
        `auction_object` INT UNSIGNED NOT NULL,
        `time` DATETIME NOT NULL
    );

ALTER TABLE `items`
ADD
    CONSTRAINT `items_user_foreign` FOREIGN KEY(`user`) REFERENCES `users`(`id`);

ALTER TABLE `images`
ADD
    CONSTRAINT `images_auction_object_foreign` FOREIGN KEY(`auction_object`) REFERENCES `ítems`(`id`);

ALTER TABLE `bids`
ADD
    CONSTRAINT `bids_auction_object_foreign` FOREIGN KEY(`auction_object`) REFERENCES `ítems`(`id`);