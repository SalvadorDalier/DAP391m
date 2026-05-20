USE [Project11DB]
GO
/****** Object:  Table [dbo].[coupon_campaigns]    Script Date: 5/20/2026 9:55:13 AM ******/
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
PRIMARY KEY CLUSTERED 
(
	[campaign_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[coupon_redemptions]    Script Date: 5/20/2026 9:55:13 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[coupon_redemptions](
	[redemption_id] [int] IDENTITY(1,1) NOT NULL,
	[campaign_id] [int] NOT NULL,
	[customer_hash] [nvarchar](16) NOT NULL,
	[redemption_date] [datetime] NULL,
PRIMARY KEY CLUSTERED 
(
	[redemption_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[customer_rfm]    Script Date: 5/20/2026 9:55:13 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[customer_rfm](
	[rfm_id] [int] IDENTITY(1,1) NOT NULL,
	[customer_hash] [nvarchar](16) NOT NULL,
	[recency] [int] NOT NULL,
	[frequency] [int] NOT NULL,
	[monetary] [decimal](12, 2) NOT NULL,
	[total_returns] [decimal](8, 2) NULL,
	[is_redeemer] [tinyint] NULL,
	[split_tag] [nvarchar](6) NULL,
	[snapshot_date] [date] NULL,
PRIMARY KEY CLUSTERED 
(
	[rfm_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[customers]    Script Date: 5/20/2026 9:55:13 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[customers](
	[customer_hash] [nvarchar](16) NOT NULL,
	[rfm_segment] [nvarchar](20) NOT NULL,
	[is_active] [tinyint] NULL,
	[created_at] [datetime2](7) NULL,
PRIMARY KEY CLUSTERED 
(
	[customer_hash] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
/****** Object:  Table [dbo].[fact_sales]    Script Date: 5/20/2026 9:55:13 AM ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[fact_sales](
	[sales_id] [int] IDENTITY(1,1) NOT NULL,
	[invoice_no] [nvarchar](20) NOT NULL,
	[customer_hash] [nvarchar](16) NULL,
	[quantity] [int] NOT NULL,
	[unit_price] [decimal](18, 2) NOT NULL,
	[invoice_date] [datetime] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[sales_id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO
ALTER TABLE [dbo].[coupon_redemptions] ADD  DEFAULT (getdate()) FOR [redemption_date]
GO
ALTER TABLE [dbo].[customer_rfm] ADD  DEFAULT ((0)) FOR [total_returns]
GO
ALTER TABLE [dbo].[customer_rfm] ADD  DEFAULT ((0)) FOR [is_redeemer]
GO
ALTER TABLE [dbo].[customer_rfm] ADD  DEFAULT ('MASTER') FOR [split_tag]
GO
ALTER TABLE [dbo].[customer_rfm] ADD  DEFAULT (getdate()) FOR [snapshot_date]
GO
ALTER TABLE [dbo].[customers] ADD  DEFAULT ((1)) FOR [is_active]
GO
ALTER TABLE [dbo].[customers] ADD  DEFAULT (getdate()) FOR [created_at]
GO
ALTER TABLE [dbo].[coupon_redemptions]  WITH CHECK ADD  CONSTRAINT [FK_red_campaign] FOREIGN KEY([campaign_id])
REFERENCES [dbo].[coupon_campaigns] ([campaign_id])
GO
ALTER TABLE [dbo].[coupon_redemptions] CHECK CONSTRAINT [FK_red_campaign]
GO
ALTER TABLE [dbo].[coupon_redemptions]  WITH CHECK ADD  CONSTRAINT [FK_red_customer] FOREIGN KEY([customer_hash])
REFERENCES [dbo].[customers] ([customer_hash])
GO
ALTER TABLE [dbo].[coupon_redemptions] CHECK CONSTRAINT [FK_red_customer]
GO
ALTER TABLE [dbo].[customer_rfm]  WITH CHECK ADD  CONSTRAINT [FK_rfm_customer] FOREIGN KEY([customer_hash])
REFERENCES [dbo].[customers] ([customer_hash])
ON DELETE CASCADE
GO
ALTER TABLE [dbo].[customer_rfm] CHECK CONSTRAINT [FK_rfm_customer]
GO
ALTER TABLE [dbo].[fact_sales]  WITH CHECK ADD  CONSTRAINT [FK_sales_customer] FOREIGN KEY([customer_hash])
REFERENCES [dbo].[customers] ([customer_hash])
GO
ALTER TABLE [dbo].[fact_sales] CHECK CONSTRAINT [FK_sales_customer]
GO
