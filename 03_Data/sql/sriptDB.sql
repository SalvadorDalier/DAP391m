USE [master]
GO
/****** Object:  Database [Project11DB]    Script Date: 5/17/2026 7:50:00 PM ******/
CREATE DATABASE [Project11DB]
 CONTAINMENT = NONE
 ON  PRIMARY 
( NAME = N'Project11DB', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\Project11DB.mdf' , SIZE = 139264KB , MAXSIZE = UNLIMITED, FILEGROWTH = 65536KB )
 LOG ON 
( NAME = N'Project11DB_log', FILENAME = N'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\Project11DB_log.ldf' , SIZE = 270336KB , MAXSIZE = 2048GB , FILEGROWTH = 65536KB )
 WITH CATALOG_COLLATION = DATABASE_DEFAULT, LEDGER = OFF
GO
ALTER DATABASE [Project11DB] SET COMPATIBILITY_LEVEL = 160
GO
IF (1 = FULLTEXTSERVICEPROPERTY('IsFullTextInstalled'))
begin
EXEC [Project11DB].[dbo].[sp_fulltext_database] @action = 'enable'
end
GO
ALTER DATABASE [Project11DB] SET ANSI_NULL_DEFAULT OFF 
GO
ALTER DATABASE [Project11DB] SET ANSI_NULLS OFF 
GO
ALTER DATABASE [Project11DB] SET ANSI_PADDING OFF 
GO
ALTER DATABASE [Project11DB] SET ANSI_WARNINGS OFF 
GO
ALTER DATABASE [Project11DB] SET ARITHABORT OFF 
GO
ALTER DATABASE [Project11DB] SET AUTO_CLOSE OFF 
GO
ALTER DATABASE [Project11DB] SET AUTO_SHRINK OFF 
GO
ALTER DATABASE [Project11DB] SET AUTO_UPDATE_STATISTICS ON 
GO
ALTER DATABASE [Project11DB] SET CURSOR_CLOSE_ON_COMMIT OFF 
GO
ALTER DATABASE [Project11DB] SET CURSOR_DEFAULT  GLOBAL 
GO
ALTER DATABASE [Project11DB] SET CONCAT_NULL_YIELDS_NULL OFF 
GO
ALTER DATABASE [Project11DB] SET NUMERIC_ROUNDABORT OFF 
GO
ALTER DATABASE [Project11DB] SET QUOTED_IDENTIFIER OFF 
GO
ALTER DATABASE [Project11DB] SET RECURSIVE_TRIGGERS OFF 
GO
ALTER DATABASE [Project11DB] SET  ENABLE_BROKER 
GO
ALTER DATABASE [Project11DB] SET AUTO_UPDATE_STATISTICS_ASYNC OFF 
GO
ALTER DATABASE [Project11DB] SET DATE_CORRELATION_OPTIMIZATION OFF 
GO
ALTER DATABASE [Project11DB] SET TRUSTWORTHY OFF 
GO
ALTER DATABASE [Project11DB] SET ALLOW_SNAPSHOT_ISOLATION OFF 
GO
ALTER DATABASE [Project11DB] SET PARAMETERIZATION SIMPLE 
GO
ALTER DATABASE [Project11DB] SET READ_COMMITTED_SNAPSHOT OFF 
GO
ALTER DATABASE [Project11DB] SET HONOR_BROKER_PRIORITY OFF 
GO
ALTER DATABASE [Project11DB] SET RECOVERY FULL 
GO
ALTER DATABASE [Project11DB] SET  MULTI_USER 
GO
ALTER DATABASE [Project11DB] SET PAGE_VERIFY CHECKSUM  
GO
ALTER DATABASE [Project11DB] SET DB_CHAINING OFF 
GO
ALTER DATABASE [Project11DB] SET FILESTREAM( NON_TRANSACTED_ACCESS = OFF ) 
GO
ALTER DATABASE [Project11DB] SET TARGET_RECOVERY_TIME = 60 SECONDS 
GO
ALTER DATABASE [Project11DB] SET DELAYED_DURABILITY = DISABLED 
GO
ALTER DATABASE [Project11DB] SET ACCELERATED_DATABASE_RECOVERY = OFF  
GO
EXEC sys.sp_db_vardecimal_storage_format N'Project11DB', N'ON'
GO
ALTER DATABASE [Project11DB] SET QUERY_STORE = ON
GO
ALTER DATABASE [Project11DB] SET QUERY_STORE (OPERATION_MODE = READ_WRITE, CLEANUP_POLICY = (STALE_QUERY_THRESHOLD_DAYS = 30), DATA_FLUSH_INTERVAL_SECONDS = 900, INTERVAL_LENGTH_MINUTES = 60, MAX_STORAGE_SIZE_MB = 1000, QUERY_CAPTURE_MODE = AUTO, SIZE_BASED_CLEANUP_MODE = AUTO, MAX_PLANS_PER_QUERY = 200, WAIT_STATS_CAPTURE_MODE = ON)
GO
USE [Project11DB]
GO
/****** Object:  User [engineer_user]    Script Date: 5/17/2026 7:50:00 PM ******/
CREATE USER [engineer_user] FOR LOGIN [engineer_login] WITH DEFAULT_SCHEMA=[dbo]
GO
/****** Object:  User [analyst_user]    Script Date: 5/17/2026 7:50:00 PM ******/
CREATE USER [analyst_user] FOR LOGIN [analyst_login] WITH DEFAULT_SCHEMA=[dbo]
GO
ALTER ROLE [db_owner] ADD MEMBER [engineer_user]
GO
/****** Object:  Table [dbo].[customers]    Script Date: 5/17/2026 7:50:01 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[customers](
	[customer_hash] [nvarchar](16) NOT NULL,
	[rfm_segment] [nvarchar](20) NOT NULL,
	[is_active] [tinyint] NOT NULL,
	[created_at] [datetime2](7) NOT NULL,
 CONSTRAINT [PK_customers] PRIMARY KEY CLUSTERED 
(
	[customer_hash] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[customer_rfm]    Script Date: 5/17/2026 7:50:01 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[customer_rfm](
	[rfm_id] [int] IDENTITY(1,1) NOT NULL,
	[customer_hash] [nvarchar](16) NOT NULL,
	[Recency] [int] NOT NULL,
	[Frequency] [int] NOT NULL,
	[Monetary] [decimal](12, 2) NOT NULL,
	[TotalReturns] [decimal](8, 2) NOT NULL,
	[Is_Redeemer] [tinyint] NOT NULL,
	[split_tag] [nvarchar](6) NOT NULL,
	[uplift_score] [decimal](6, 4) NULL,
	[model_label] [nvarchar](14) NULL,
	[snapshot_date] [date] NOT NULL,
 CONSTRAINT [PK_rfm] PRIMARY KEY CLUSTERED 
(
	[rfm_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  View [dbo].[vw_customer_full]    Script Date: 5/17/2026 7:50:01 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


-- ═══════════════════════════════════════════════════════════
--  SECTION 5: VIEWS
-- ═══════════════════════════════════════════════════════════

-- View 1: Thong tin day du customer (EDA + feature engineering)
CREATE VIEW [dbo].[vw_customer_full] AS
SELECT
    c.customer_hash,
    c.rfm_segment,
    r.Recency,
    r.Frequency,
    r.Monetary,
    r.TotalReturns,
    r.Is_Redeemer,
    r.split_tag,
    r.uplift_score,
    r.model_label
FROM customers    c
JOIN customer_rfm r ON r.customer_hash = c.customer_hash;
GO
/****** Object:  View [dbo].[vw_redemption_summary]    Script Date: 5/17/2026 7:50:01 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- View 2: Ty le redemption theo phan khuc & split (SQL Query 1)
CREATE VIEW [dbo].[vw_redemption_summary] AS
SELECT
    c.rfm_segment,
    r.split_tag,
    COUNT(*)                                                          AS total_customers,
    SUM(r.Is_Redeemer)                                                AS total_redeemed,
    ROUND(SUM(r.Is_Redeemer) * 100.0 / NULLIF(COUNT(*), 0), 4)      AS redemption_rate_pct,
    ROUND(AVG(CAST(r.Recency    AS FLOAT)), 2)                        AS avg_recency,
    ROUND(AVG(CAST(r.Frequency  AS FLOAT)), 2)                        AS avg_frequency,
    ROUND(AVG(r.Monetary), 2)                                         AS avg_monetary
FROM customer_rfm r
JOIN customers    c ON c.customer_hash = r.customer_hash
GROUP BY c.rfm_segment, r.split_tag;
GO
/****** Object:  View [dbo].[vw_segment_roi]    Script Date: 5/17/2026 7:50:01 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

-- View 3: ROI theo phan khuc (Cost-Benefit Buoc 3 + Power BI)
CREATE VIEW [dbo].[vw_segment_roi] AS
SELECT
    c.rfm_segment,
    r.split_tag,
    COUNT(*)                                            AS n_customers,
    SUM(r.Is_Redeemer)                                  AS n_redeemers,
    ROUND(AVG(CAST(r.Recency   AS FLOAT)), 2)           AS avg_recency,
    ROUND(AVG(CAST(r.Frequency AS FLOAT)), 2)           AS avg_frequency,
    ROUND(AVG(r.Monetary),  2)                          AS avg_monetary,
    ROUND(AVG(r.TotalReturns), 2)                       AS avg_returns,
    ROUND(SUM(r.Monetary),  2)                          AS total_revenue_gbp,
    ROUND(
        SUM(r.Is_Redeemer) * 100.0 / NULLIF(COUNT(*), 0), 4
    )                                                   AS redemption_rate_pct
FROM customer_rfm r
JOIN customers    c ON c.customer_hash = r.customer_hash
GROUP BY c.rfm_segment, r.split_tag;
GO
/****** Object:  Table [dbo].[coupon_campaigns]    Script Date: 5/17/2026 7:50:01 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[coupon_campaigns](
	[campaign_id] [int] IDENTITY(1,1) NOT NULL,
	[campaign_name] [nvarchar](100) NOT NULL,
	[coupon_type] [nvarchar](30) NOT NULL,
	[discount_value] [decimal](6, 2) NOT NULL,
	[start_date] [date] NOT NULL,
	[end_date] [date] NOT NULL,
	[budget_gbp] [decimal](12, 2) NULL,
	[target_segment] [nvarchar](20) NULL,
 CONSTRAINT [PK_campaign] PRIMARY KEY CLUSTERED 
(
	[campaign_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[dim_countries]    Script Date: 5/17/2026 7:50:01 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[dim_countries](
	[country_id] [int] IDENTITY(1,1) NOT NULL,
	[country_name] [nvarchar](100) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[country_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[country_name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[dim_products]    Script Date: 5/17/2026 7:50:01 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[dim_products](
	[stock_code] [nvarchar](50) NOT NULL,
	[description] [nvarchar](255) NULL,
PRIMARY KEY CLUSTERED 
(
	[stock_code] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[fact_sales]    Script Date: 5/17/2026 7:50:01 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[fact_sales](
	[sales_id] [int] IDENTITY(1,1) NOT NULL,
	[invoice_no] [nvarchar](20) NOT NULL,
	[stock_code] [nvarchar](50) NOT NULL,
	[customer_id] [int] NULL,
	[quantity] [int] NOT NULL,
	[unit_price] [decimal](18, 2) NOT NULL,
	[invoice_date] [datetime] NOT NULL,
	[country_id] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[sales_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[online_retail]    Script Date: 5/17/2026 7:50:01 PM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[online_retail](
	[InvoiceNo] [varchar](max) NULL,
	[StockCode] [varchar](max) NULL,
	[Description] [varchar](max) NULL,
	[Quantity] [bigint] NULL,
	[InvoiceDate] [varchar](max) NULL,
	[UnitPrice] [float] NULL,
	[CustomerID] [float] NULL,
	[Country] [varchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IDX_rfm_hash]    Script Date: 5/17/2026 7:50:01 PM ******/
CREATE NONCLUSTERED INDEX [IDX_rfm_hash] ON [dbo].[customer_rfm]
(
	[customer_hash] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
/****** Object:  Index [IDX_rfm_redeem]    Script Date: 5/17/2026 7:50:01 PM ******/
CREATE NONCLUSTERED INDEX [IDX_rfm_redeem] ON [dbo].[customer_rfm]
(
	[Is_Redeemer] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IDX_rfm_split]    Script Date: 5/17/2026 7:50:01 PM ******/
CREATE NONCLUSTERED INDEX [IDX_rfm_split] ON [dbo].[customer_rfm]
(
	[split_tag] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
SET ANSI_PADDING ON
GO
/****** Object:  Index [IDX_seg]    Script Date: 5/17/2026 7:50:01 PM ******/
CREATE NONCLUSTERED INDEX [IDX_seg] ON [dbo].[customers]
(
	[rfm_segment] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, SORT_IN_TEMPDB = OFF, DROP_EXISTING = OFF, ONLINE = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
GO
ALTER TABLE [dbo].[customer_rfm] ADD  DEFAULT ((0.00)) FOR [TotalReturns]
GO
ALTER TABLE [dbo].[customer_rfm] ADD  DEFAULT ((0)) FOR [Is_Redeemer]
GO
ALTER TABLE [dbo].[customer_rfm] ADD  DEFAULT ('MASTER') FOR [split_tag]
GO
ALTER TABLE [dbo].[customer_rfm] ADD  DEFAULT (CONVERT([date],sysdatetime())) FOR [snapshot_date]
GO
ALTER TABLE [dbo].[customers] ADD  DEFAULT ((1)) FOR [is_active]
GO
ALTER TABLE [dbo].[customers] ADD  DEFAULT (sysdatetime()) FOR [created_at]
GO
ALTER TABLE [dbo].[customer_rfm]  WITH CHECK ADD  CONSTRAINT [FK_rfm_customer] FOREIGN KEY([customer_hash])
REFERENCES [dbo].[customers] ([customer_hash])
ON UPDATE CASCADE
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[customer_rfm] CHECK CONSTRAINT [FK_rfm_customer]
GO
ALTER TABLE [dbo].[fact_sales]  WITH CHECK ADD  CONSTRAINT [FK_sales_country] FOREIGN KEY([country_id])
REFERENCES [dbo].[dim_countries] ([country_id])
GO
ALTER TABLE [dbo].[fact_sales] CHECK CONSTRAINT [FK_sales_country]
GO
ALTER TABLE [dbo].[fact_sales]  WITH CHECK ADD  CONSTRAINT [FK_sales_product] FOREIGN KEY([stock_code])
REFERENCES [dbo].[dim_products] ([stock_code])
GO
ALTER TABLE [dbo].[fact_sales] CHECK CONSTRAINT [FK_sales_product]
GO
ALTER TABLE [dbo].[coupon_campaigns]  WITH CHECK ADD  CONSTRAINT [CHK_coupon_type] CHECK  (([coupon_type]='BOGO' OR [coupon_type]='FreeShipping' OR [coupon_type]='FixedOff' OR [coupon_type]='PercentOff'))
GO
ALTER TABLE [dbo].[coupon_campaigns] CHECK CONSTRAINT [CHK_coupon_type]
GO
ALTER TABLE [dbo].[coupon_campaigns]  WITH CHECK ADD  CONSTRAINT [CHK_dates] CHECK  (([end_date]>=[start_date]))
GO
ALTER TABLE [dbo].[coupon_campaigns] CHECK CONSTRAINT [CHK_dates]
GO
ALTER TABLE [dbo].[coupon_campaigns]  WITH CHECK ADD  CONSTRAINT [CHK_discount] CHECK  (([discount_value]>(0)))
GO
ALTER TABLE [dbo].[coupon_campaigns] CHECK CONSTRAINT [CHK_discount]
GO
ALTER TABLE [dbo].[coupon_campaigns]  WITH CHECK ADD  CONSTRAINT [CHK_target_seg] CHECK  (([target_segment]='All' OR [target_segment]='Lost' OR [target_segment]='At Risk' OR [target_segment]='Loyal' OR [target_segment]='Champions' OR [target_segment] IS NULL))
GO
ALTER TABLE [dbo].[coupon_campaigns] CHECK CONSTRAINT [CHK_target_seg]
GO
ALTER TABLE [dbo].[customer_rfm]  WITH CHECK ADD  CONSTRAINT [CHK_frequency] CHECK  (([Frequency]>=(1)))
GO
ALTER TABLE [dbo].[customer_rfm] CHECK CONSTRAINT [CHK_frequency]
GO
ALTER TABLE [dbo].[customer_rfm]  WITH CHECK ADD  CONSTRAINT [CHK_label] CHECK  (([model_label]='Do Not Target' OR [model_label]='Target' OR [model_label] IS NULL))
GO
ALTER TABLE [dbo].[customer_rfm] CHECK CONSTRAINT [CHK_label]
GO
ALTER TABLE [dbo].[customer_rfm]  WITH CHECK ADD  CONSTRAINT [CHK_monetary] CHECK  (([Monetary]>=(0)))
GO
ALTER TABLE [dbo].[customer_rfm] CHECK CONSTRAINT [CHK_monetary]
GO
ALTER TABLE [dbo].[customer_rfm]  WITH CHECK ADD  CONSTRAINT [CHK_recency] CHECK  (([Recency]>=(0)))
GO
ALTER TABLE [dbo].[customer_rfm] CHECK CONSTRAINT [CHK_recency]
GO
ALTER TABLE [dbo].[customer_rfm]  WITH CHECK ADD  CONSTRAINT [CHK_redeemer] CHECK  (([Is_Redeemer]=(1) OR [Is_Redeemer]=(0)))
GO
ALTER TABLE [dbo].[customer_rfm] CHECK CONSTRAINT [CHK_redeemer]
GO
ALTER TABLE [dbo].[customer_rfm]  WITH CHECK ADD  CONSTRAINT [CHK_split] CHECK  (([split_tag]='MASTER' OR [split_tag]='TEST' OR [split_tag]='TRAIN'))
GO
ALTER TABLE [dbo].[customer_rfm] CHECK CONSTRAINT [CHK_split]
GO
ALTER TABLE [dbo].[customers]  WITH CHECK ADD  CONSTRAINT [CHK_active] CHECK  (([is_active]=(1) OR [is_active]=(0)))
GO
ALTER TABLE [dbo].[customers] CHECK CONSTRAINT [CHK_active]
GO
ALTER TABLE [dbo].[customers]  WITH CHECK ADD  CONSTRAINT [CHK_segment] CHECK  (([rfm_segment]='Lost' OR [rfm_segment]='At Risk' OR [rfm_segment]='Loyal' OR [rfm_segment]='Champions'))
GO
ALTER TABLE [dbo].[customers] CHECK CONSTRAINT [CHK_segment]
GO
USE [master]
GO
ALTER DATABASE [Project11DB] SET  READ_WRITE 
GO
