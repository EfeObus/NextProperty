-- MySQL dump 10.13  Distrib 8.4.0, for macos13.2 (arm64)
--
-- Host: localhost    Database: nextproperty_ai
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `agent_reviews`
--

DROP TABLE IF EXISTS `agent_reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agent_reviews` (
  `id` int NOT NULL AUTO_INCREMENT,
  `agent_id` varchar(50) NOT NULL,
  `reviewer_name` varchar(100) DEFAULT NULL,
  `rating` int DEFAULT NULL,
  `review_text` text,
  `transaction_type` varchar(20) DEFAULT NULL,
  `property_type` varchar(50) DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `agent_id` (`agent_id`),
  CONSTRAINT `agent_reviews_ibfk_1` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`agent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `agents`
--

DROP TABLE IF EXISTS `agents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agents` (
  `agent_id` varchar(50) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(120) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `license_number` varchar(50) DEFAULT NULL,
  `brokerage` varchar(100) DEFAULT NULL,
  `specialties` text,
  `years_experience` int DEFAULT NULL,
  `languages` varchar(200) DEFAULT NULL,
  `website` varchar(200) DEFAULT NULL,
  `bio` text,
  `profile_photo` varchar(500) DEFAULT NULL,
  `total_sales` int DEFAULT NULL,
  `total_volume` decimal(15,2) DEFAULT NULL,
  `average_dom` decimal(5,2) DEFAULT NULL,
  `client_satisfaction` decimal(3,2) DEFAULT NULL,
  `service_areas` text,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`agent_id`),
  UNIQUE KEY `ix_agents_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `economic_data`
--

DROP TABLE IF EXISTS `economic_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `economic_data` (
  `id` int NOT NULL AUTO_INCREMENT,
  `indicator_name` varchar(100) NOT NULL,
  `indicator_code` varchar(50) NOT NULL,
  `source` varchar(50) NOT NULL,
  `date` date NOT NULL,
  `value` decimal(15,6) DEFAULT NULL,
  `unit` varchar(50) DEFAULT NULL,
  `description` text,
  `frequency` varchar(20) DEFAULT NULL,
  `seasonal_adjustment` varchar(50) DEFAULT NULL,
  `is_preliminary` tinyint(1) DEFAULT NULL,
  `is_revised` tinyint(1) DEFAULT NULL,
  `data_quality` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_indicator_date` (`indicator_code`,`date`),
  KEY `idx_source_date` (`source`,`date`),
  KEY `ix_economic_data_indicator_code` (`indicator_code`),
  KEY `ix_economic_data_date` (`date`),
  KEY `idx_name_date` (`indicator_name`,`date`),
  KEY `ix_economic_data_indicator_name` (`indicator_name`)
) ENGINE=InnoDB AUTO_INCREMENT=261 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `economic_indicators`
--

DROP TABLE IF EXISTS `economic_indicators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `economic_indicators` (
  `id` int NOT NULL AUTO_INCREMENT,
  `indicator_code` varchar(50) NOT NULL,
  `indicator_name` varchar(200) NOT NULL,
  `source` varchar(50) NOT NULL,
  `category` varchar(100) DEFAULT NULL,
  `description` text,
  `frequency` varchar(20) DEFAULT NULL,
  `unit` varchar(50) DEFAULT NULL,
  `seasonal_adjustment` varchar(50) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `last_updated` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `update_frequency` varchar(20) DEFAULT NULL,
  `priority` int DEFAULT NULL,
  `ml_relevance` decimal(3,2) DEFAULT NULL,
  `property_impact` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_economic_indicators_indicator_code` (`indicator_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `properties`
--

DROP TABLE IF EXISTS `properties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `properties` (
  `listing_id` varchar(50) NOT NULL,
  `mls` varchar(20) DEFAULT NULL,
  `property_type` varchar(50) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `province` varchar(50) DEFAULT NULL,
  `postal_code` varchar(10) DEFAULT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `sold_price` decimal(12,2) DEFAULT NULL,
  `original_price` decimal(12,2) DEFAULT NULL,
  `price_per_sqft` decimal(8,2) DEFAULT NULL,
  `bedrooms` int DEFAULT NULL,
  `bathrooms` decimal(3,1) DEFAULT NULL,
  `kitchens_plus` int DEFAULT NULL,
  `rooms` int DEFAULT NULL,
  `sqft` int DEFAULT NULL,
  `lot_size` decimal(10,2) DEFAULT NULL,
  `year_built` int DEFAULT NULL,
  `sold_date` date DEFAULT NULL,
  `dom` int DEFAULT NULL,
  `taxes` decimal(10,2) DEFAULT NULL,
  `maintenance_fee` decimal(10,2) DEFAULT NULL,
  `features` text,
  `community_features` text,
  `remarks` text,
  `ai_valuation` decimal(12,2) DEFAULT NULL,
  `investment_score` decimal(3,2) DEFAULT NULL,
  `risk_assessment` varchar(20) DEFAULT NULL,
  `market_trend` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `agent_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`listing_id`),
  KEY `agent_id` (`agent_id`),
  KEY `ix_properties_city` (`city`),
  KEY `ix_properties_sold_date` (`sold_date`),
  KEY `idx_location` (`latitude`,`longitude`),
  KEY `idx_property_search` (`city`,`property_type`,`sold_price`),
  KEY `idx_date_type` (`sold_date`,`property_type`),
  KEY `ix_properties_year_built` (`year_built`),
  KEY `ix_properties_sold_price` (`sold_price`),
  KEY `idx_price_range` (`sold_price`),
  KEY `ix_properties_mls` (`mls`),
  KEY `ix_properties_property_type` (`property_type`),
  KEY `idx_ai_valuation` (`ai_valuation`),
  KEY `idx_original_price` (`original_price`),
  KEY `idx_sqft_bedrooms` (`sqft`,`bedrooms`),
  KEY `idx_city_type_price` (`city`(50),`property_type`(20),`original_price`),
  KEY `idx_investment_score` (`investment_score`),
  CONSTRAINT `properties_ibfk_1` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`agent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `property_photos`
--

DROP TABLE IF EXISTS `property_photos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `property_photos` (
  `id` int NOT NULL AUTO_INCREMENT,
  `listing_id` varchar(50) NOT NULL,
  `photo_url` varchar(500) NOT NULL,
  `photo_type` varchar(50) DEFAULT NULL,
  `order_index` int DEFAULT NULL,
  `caption` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `listing_id` (`listing_id`),
  CONSTRAINT `property_photos_ibfk_1` FOREIGN KEY (`listing_id`) REFERENCES `properties` (`listing_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `property_rooms`
--

DROP TABLE IF EXISTS `property_rooms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `property_rooms` (
  `id` int NOT NULL AUTO_INCREMENT,
  `listing_id` varchar(50) NOT NULL,
  `room_type` varchar(50) DEFAULT NULL,
  `level` varchar(20) DEFAULT NULL,
  `dimensions` varchar(50) DEFAULT NULL,
  `features` text,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `listing_id` (`listing_id`),
  CONSTRAINT `property_rooms_ibfk_1` FOREIGN KEY (`listing_id`) REFERENCES `properties` (`listing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `saved_properties`
--

DROP TABLE IF EXISTS `saved_properties`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `saved_properties` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `listing_id` varchar(50) NOT NULL,
  `notes` text,
  `tags` varchar(200) DEFAULT NULL,
  `is_favorite` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_user_property` (`user_id`,`listing_id`),
  KEY `listing_id` (`listing_id`),
  CONSTRAINT `saved_properties_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `saved_properties_ibfk_2` FOREIGN KEY (`listing_id`) REFERENCES `properties` (`listing_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `search_history`
--

DROP TABLE IF EXISTS `search_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `search_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `search_query` varchar(500) DEFAULT NULL,
  `search_filters` text,
  `results_count` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `search_history_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) NOT NULL,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `profile_picture` varchar(500) DEFAULT NULL,
  `preferred_cities` text,
  `preferred_property_types` text,
  `price_range_min` decimal(12,2) DEFAULT NULL,
  `price_range_max` decimal(12,2) DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_verified` tinyint(1) DEFAULT NULL,
  `last_login` datetime DEFAULT NULL,
  `login_count` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping routines for database 'nextproperty_ai'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-11 20:38:58
