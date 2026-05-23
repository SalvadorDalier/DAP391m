-- ==============================================================================
-- Project11DB Creation Script
-- ==============================================================================
-- IMPORTANT: Run this entire script in SSMS to create the database and schema.
-- ==============================================================================

USE master;
GO

-- ==============================================================================
-- 1. Database Creation
-- ==============================================================================
IF DB_ID('Project11DB') IS NOT NULL
BEGIN
    PRINT 'Database Project11DB already exists. Dropping it first...';
    ALTER DATABASE Project11DB SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE Project11DB;
END
GO

PRINT 'Creating database Project11DB...';
CREATE DATABASE Project11DB COLLATE SQL_Latin1_General_CP1_CI_AS;
GO

ALTER DATABASE Project11DB SET RECOVERY FULL;
GO

USE Project11DB;
GO

-- ==============================================================================
-- 2. Schema Organization
-- ==============================================================================
PRINT 'Creating Schemas...';
GO
CREATE SCHEMA raw;
GO
CREATE SCHEMA core;
GO
CREATE SCHEMA security;
GO
CREATE SCHEMA analytics;
GO

-- ==============================================================================
-- 4. Data Encryption Setup
-- ==============================================================================
-- Note: SQL Server requires a password to create a Database Master Key. 
-- A generic placeholder is used here as requested.
PRINT 'Setting up Encryption...';
GO
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'PlaceholderPassword123!';
GO

CREATE CERTIFICATE CustomerPII_Cert 
    WITH SUBJECT = 'Customer PII Encryption Certificate';
GO

CREATE SYMMETRIC KEY CustomerPII_Key
    WITH ALGORITHM = AES_256
    ENCRYPTION BY CERTIFICATE CustomerPII_Cert;
GO

-- ==============================================================================
-- 3 & 5. Core Tables & Constraints
-- ==============================================================================
PRINT 'Creating Tables...';
GO

-- raw.OnlineRetail
CREATE TABLE raw.OnlineRetail (
    InvoiceNo NVARCHAR(50),
    StockCode NVARCHAR(50),
    Description NVARCHAR(500),
    Quantity NVARCHAR(50),
    InvoiceDate NVARCHAR(50),
    Price NVARCHAR(50),
    CustomerID NVARCHAR(50),
    Country NVARCHAR(100)
);
GO

-- core.Customer
CREATE TABLE core.Customer (
    CustomerID NVARCHAR(50) NOT NULL CONSTRAINT PK_Customer PRIMARY KEY,
    Country NVARCHAR(100),
    EncryptedEmail VARBINARY(256),
    EncryptedPhone VARBINARY(256),
    CreatedAt DATETIME2 NOT NULL CONSTRAINT DF_Customer_CreatedAt DEFAULT SYSDATETIME(),
    UpdatedAt DATETIME2 NOT NULL CONSTRAINT DF_Customer_UpdatedAt DEFAULT SYSDATETIME()
);
GO

-- core.[Transaction]
CREATE TABLE core.[Transaction] (
    TransactionID BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Transaction PRIMARY KEY,
    InvoiceNo NVARCHAR(50) NOT NULL,
    CustomerID NVARCHAR(50) NOT NULL CONSTRAINT FK_Transaction_Customer REFERENCES core.Customer(CustomerID) ON DELETE NO ACTION ON UPDATE CASCADE,
    InvoiceDate DATETIME2 NOT NULL,
    TotalAmount DECIMAL(18,4) NOT NULL,
    CONSTRAINT CHK_Transaction_TotalAmount CHECK (TotalAmount > 0),
    CONSTRAINT CHK_Transaction_InvoiceDate CHECK (InvoiceDate <= GETDATE())
);
GO

-- core.TransactionItem
CREATE TABLE core.TransactionItem (
    ItemID BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_TransactionItem PRIMARY KEY,
    TransactionID BIGINT NOT NULL CONSTRAINT FK_TransactionItem_Transaction REFERENCES core.[Transaction](TransactionID) ON DELETE CASCADE,
    StockCode NVARCHAR(50) NOT NULL,
    Description NVARCHAR(500),
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(18,4) NOT NULL,
    LineTotal AS (CAST(Quantity * UnitPrice AS DECIMAL(18,4))) PERSISTED,
    CONSTRAINT CHK_TransactionItem_Quantity CHECK (Quantity > 0),
    CONSTRAINT CHK_TransactionItem_UnitPrice CHECK (UnitPrice >= 0)
);
GO

-- core.Coupon
CREATE TABLE core.Coupon (
    CouponID INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_Coupon PRIMARY KEY,
    CouponCode NVARCHAR(50) NOT NULL CONSTRAINT UQ_Coupon_Code UNIQUE,
    CouponType NVARCHAR(20) NOT NULL,
    DiscountValue DECIMAL(10,4) NOT NULL,
    MinOrderValue DECIMAL(18,4),
    ValidFrom DATE NOT NULL,
    ValidTo DATE NOT NULL,
    IsActive BIT NOT NULL CONSTRAINT DF_Coupon_IsActive DEFAULT 1,
    CONSTRAINT CHK_Coupon_Type CHECK (CouponType IN ('PERCENTAGE','FIXED','BOGO','FREESHIP')),
    CONSTRAINT CHK_Coupon_ValidDates CHECK (ValidTo > ValidFrom),
    CONSTRAINT CHK_Coupon_Discount CHECK (
        (CouponType = 'PERCENTAGE' AND DiscountValue BETWEEN 0 AND 100) OR 
        (CouponType <> 'PERCENTAGE')
    )
);
GO

-- core.CouponIssuance
CREATE TABLE core.CouponIssuance (
    IssuanceID BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_CouponIssuance PRIMARY KEY,
    CustomerID NVARCHAR(50) NOT NULL CONSTRAINT FK_CouponIssuance_Customer REFERENCES core.Customer(CustomerID),
    CouponID INT NOT NULL CONSTRAINT FK_CouponIssuance_Coupon REFERENCES core.Coupon(CouponID),
    IssuedAt DATETIME2 NOT NULL CONSTRAINT DF_CouponIssuance_IssuedAt DEFAULT SYSDATETIME(),
    IsRedeemed BIT NOT NULL CONSTRAINT DF_CouponIssuance_IsRedeemed DEFAULT 0,
    RedeemedAt DATETIME2 NULL,
    RedeemedTransactionID BIGINT NULL CONSTRAINT FK_CouponIssuance_RedeemedTransaction REFERENCES core.[Transaction](TransactionID),
    CONSTRAINT UQ_CouponIssuance_CustCoupon UNIQUE (CustomerID, CouponID),
    CONSTRAINT CHK_CouponIssuance_RedeemedLogic CHECK (
        (IsRedeemed = 1 AND RedeemedAt IS NOT NULL) OR 
        (IsRedeemed = 0 AND RedeemedAt IS NULL)
    ),
    CONSTRAINT CHK_CouponIssuance_RedeemedDate CHECK (RedeemedAt >= IssuedAt)
);
GO

-- analytics.CustomerRFM
CREATE TABLE analytics.CustomerRFM (
    CustomerID NVARCHAR(50) NOT NULL CONSTRAINT FK_CustomerRFM_Customer REFERENCES core.Customer(CustomerID),
    SnapshotDate DATE NOT NULL,
    Recency INT NOT NULL,
    Frequency INT NOT NULL,
    Monetary DECIMAL(18,4) NOT NULL,
    R_Score TINYINT NOT NULL,
    F_Score TINYINT NOT NULL,
    M_Score TINYINT NOT NULL,
    RFM_Segment NVARCHAR(50) NOT NULL,
    RFM_Score AS (CAST(R_Score + F_Score + M_Score AS TINYINT)) PERSISTED,
    CONSTRAINT PK_CustomerRFM PRIMARY KEY (CustomerID, SnapshotDate),
    CONSTRAINT CHK_CustomerRFM_Scores CHECK (
        R_Score BETWEEN 1 AND 5 AND 
        F_Score BETWEEN 1 AND 5 AND 
        M_Score BETWEEN 1 AND 5
    )
);
GO

-- security.AuditLog
CREATE TABLE security.AuditLog (
    AuditID BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_AuditLog PRIMARY KEY,
    TableName NVARCHAR(128) NOT NULL,
    Operation NVARCHAR(10) NOT NULL,
    RecordID BIGINT NOT NULL,
    ChangedBy NVARCHAR(128) NOT NULL CONSTRAINT DF_AuditLog_ChangedBy DEFAULT SYSTEM_USER,
    ChangedAt DATETIME2 NOT NULL CONSTRAINT DF_AuditLog_ChangedAt DEFAULT SYSDATETIME(),
    OldValues NVARCHAR(MAX),
    NewValues NVARCHAR(MAX)
);
GO

-- ==============================================================================
-- 6. Indexes
-- ==============================================================================
PRINT 'Creating Indexes...';
GO

CREATE NONCLUSTERED INDEX IX_Transaction_CustomerID_Date 
ON core.[Transaction](CustomerID, InvoiceDate);
GO

CREATE NONCLUSTERED INDEX IX_CouponIssuance_CustomerID_IsRedeemed 
ON core.CouponIssuance(CustomerID, IsRedeemed) INCLUDE (CouponID);
GO

CREATE NONCLUSTERED INDEX IX_CustomerRFM_Segment 
ON analytics.CustomerRFM(RFM_Segment) INCLUDE (Recency, Frequency, Monetary);
GO

CREATE NONCLUSTERED INDEX IX_AuditLog_TableName_ChangedAt 
ON security.AuditLog(TableName, ChangedAt);
GO

-- ==============================================================================
-- 7. Triggers
-- ==============================================================================
PRINT 'Creating Triggers...';
GO

CREATE TRIGGER core.tr_Customer_UpdateTimestamp
ON core.Customer
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE c
    SET UpdatedAt = SYSDATETIME()
    FROM core.Customer c
    INNER JOIN inserted i ON c.CustomerID = i.CustomerID;
END
GO

CREATE TRIGGER core.tr_CouponIssuance_RedeemCheck
ON core.CouponIssuance
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    -- Auto-set RedeemedAt if IsRedeemed flips to 1 and date is null
    IF UPDATE(IsRedeemed)
    BEGIN
        UPDATE ci
        SET RedeemedAt = SYSDATETIME()
        FROM core.CouponIssuance ci
        INNER JOIN inserted i ON ci.IssuanceID = i.IssuanceID
        WHERE i.IsRedeemed = 1 AND ci.RedeemedAt IS NULL;
    END
END
GO

CREATE TRIGGER core.tr_CouponIssuance_Audit
ON core.CouponIssuance
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Operation NVARCHAR(10);
    
    IF EXISTS(SELECT * FROM inserted) AND EXISTS(SELECT * FROM deleted)
        SET @Operation = 'UPDATE';
    ELSE IF EXISTS(SELECT * FROM inserted)
        SET @Operation = 'INSERT';
    ELSE
        SET @Operation = 'DELETE';

    IF @Operation = 'INSERT'
    BEGIN
        INSERT INTO security.AuditLog (TableName, Operation, RecordID, NewValues)
        SELECT 'core.CouponIssuance', @Operation, IssuanceID,
               (SELECT * FROM inserted i2 WHERE i2.IssuanceID = i.IssuanceID FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
        FROM inserted i;
    END
    ELSE IF @Operation = 'UPDATE'
    BEGIN
        INSERT INTO security.AuditLog (TableName, Operation, RecordID, OldValues, NewValues)
        SELECT 'core.CouponIssuance', @Operation, i.IssuanceID,
               (SELECT * FROM deleted d2 WHERE d2.IssuanceID = i.IssuanceID FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
               (SELECT * FROM inserted i2 WHERE i2.IssuanceID = i.IssuanceID FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
        FROM inserted i;
    END
    ELSE IF @Operation = 'DELETE'
    BEGIN
        INSERT INTO security.AuditLog (TableName, Operation, RecordID, OldValues)
        SELECT 'core.CouponIssuance', @Operation, IssuanceID,
               (SELECT * FROM deleted d2 WHERE d2.IssuanceID = d.IssuanceID FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)
        FROM deleted d;
    END
END
GO

-- ==============================================================================
-- 8. Stored Procedures
-- ==============================================================================
PRINT 'Creating Stored Procedures...';
GO

-- Encryption SPs
CREATE OR ALTER PROCEDURE security.sp_EncryptCustomerPII
    @CustomerID NVARCHAR(50),
    @Email NVARCHAR(256),
    @Phone NVARCHAR(256)
AS
BEGIN
    SET NOCOUNT ON;
    OPEN SYMMETRIC KEY CustomerPII_Key DECRYPTION BY CERTIFICATE CustomerPII_Cert;
    
    UPDATE core.Customer
    SET EncryptedEmail = ENCRYPTBYKEY(KEY_GUID('CustomerPII_Key'), @Email),
        EncryptedPhone = ENCRYPTBYKEY(KEY_GUID('CustomerPII_Key'), @Phone)
    WHERE CustomerID = @CustomerID;
    
    CLOSE SYMMETRIC KEY CustomerPII_Key;
END
GO

CREATE OR ALTER PROCEDURE security.sp_DecryptCustomerPII
    @CustomerID NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    OPEN SYMMETRIC KEY CustomerPII_Key DECRYPTION BY CERTIFICATE CustomerPII_Cert;
    
    SELECT 
        CustomerID,
        CAST(DECRYPTBYKEY(EncryptedEmail) AS NVARCHAR(256)) AS PlaintextEmail,
        CAST(DECRYPTBYKEY(EncryptedPhone) AS NVARCHAR(256)) AS PlaintextPhone
    FROM core.Customer
    WHERE CustomerID = @CustomerID;
    
    CLOSE SYMMETRIC KEY CustomerPII_Key;
END
GO

-- Data Logic SPs
CREATE OR ALTER PROCEDURE core.sp_ImportRawData
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRY
        BEGIN TRANSACTION;
        
        -- Insert new Customers
        INSERT INTO core.Customer (CustomerID, Country)
        SELECT DISTINCT CustomerID, Country
        FROM raw.OnlineRetail
        WHERE CustomerID IS NOT NULL AND CustomerID NOT IN (SELECT CustomerID FROM core.Customer);

        -- Assume further normalization into Transaction and TransactionItem happens here
        -- In a real scenario, we would parse InvoiceDate, cast types, and insert into core tables.
        
        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

CREATE OR ALTER PROCEDURE analytics.sp_CalculateRFM
    @SnapshotDate DATE
AS
BEGIN
    SET NOCOUNT ON;
    PRINT 'Calculating RFM...';
    -- Stub procedure: normally contains aggregation logic to insert into analytics.CustomerRFM
END
GO

CREATE OR ALTER PROCEDURE core.sp_IssueCoupon
    @CustomerID NVARCHAR(50),
    @CouponType NVARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @CouponID INT = (SELECT TOP 1 CouponID FROM core.Coupon WHERE CouponType = @CouponType AND IsActive = 1);
    IF @CouponID IS NOT NULL
    BEGIN
        INSERT INTO core.CouponIssuance (CustomerID, CouponID)
        VALUES (@CustomerID, @CouponID);
    END
END
GO

CREATE OR ALTER PROCEDURE core.sp_RedeemCoupon
    @IssuanceID BIGINT,
    @TransactionID BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE core.CouponIssuance
    SET IsRedeemed = 1, RedeemedTransactionID = @TransactionID, RedeemedAt = SYSDATETIME()
    WHERE IssuanceID = @IssuanceID AND IsRedeemed = 0;
END
GO

CREATE OR ALTER PROCEDURE analytics.sp_GetModelFeatures
    @SnapshotDate DATE
AS
BEGIN
    SET NOCOUNT ON;
    -- Select feature matrix joined from RFM and CouponIssuance
    SELECT 
        r.CustomerID, r.Recency, r.Frequency, r.Monetary, r.RFM_Segment,
        c.CouponType, c.DiscountValue,
        i.IsRedeemed
    FROM analytics.CustomerRFM r
    INNER JOIN core.CouponIssuance i ON r.CustomerID = i.CustomerID
    INNER JOIN core.Coupon c ON i.CouponID = c.CouponID
    WHERE r.SnapshotDate = @SnapshotDate;
END
GO

-- ==============================================================================
-- 9. Views
-- ==============================================================================
PRINT 'Creating Views...';
GO

CREATE OR ALTER VIEW analytics.vw_CouponRedemptionRate
AS
SELECT 
    c.CouponType,
    COUNT(i.IssuanceID) AS TotalIssued,
    SUM(CAST(i.IsRedeemed AS INT)) AS TotalRedeemed,
    CAST(SUM(CAST(i.IsRedeemed AS INT)) AS FLOAT) / NULLIF(COUNT(i.IssuanceID), 0) AS RedemptionRate
FROM core.CouponIssuance i
INNER JOIN core.Coupon c ON i.CouponID = c.CouponID
GROUP BY c.CouponType;
GO

CREATE OR ALTER VIEW analytics.vw_ActiveCoupons
AS
SELECT *
FROM core.Coupon
WHERE IsActive = 1 AND GETDATE() BETWEEN ValidFrom AND ValidTo;
GO

CREATE OR ALTER VIEW analytics.vw_CustomerFeatureMatrix
AS
SELECT 
    r.CustomerID, r.RFM_Segment, r.RFM_Score,
    c.CouponCode, c.DiscountValue,
    i.IsRedeemed, i.IssuedAt
FROM analytics.CustomerRFM r
INNER JOIN core.CouponIssuance i ON r.CustomerID = i.CustomerID
INNER JOIN core.Coupon c ON i.CouponID = c.CouponID;
GO

-- ==============================================================================
-- 10. Sample Data
-- ==============================================================================
PRINT 'Inserting Sample Data...';
GO

BEGIN TRY
    BEGIN TRANSACTION;

    -- Insert Customers
    INSERT INTO core.Customer (CustomerID, Country) VALUES 
    ('CUST001', 'UK'), ('CUST002', 'USA'), ('CUST003', 'Germany'), 
    ('CUST004', 'UK'), ('CUST005', 'France'), ('CUST006', 'Spain'),
    ('CUST007', 'UK'), ('CUST008', 'Italy'), ('CUST009', 'USA'), ('CUST010', 'Japan');

    -- Encrypt sample PII
    EXEC security.sp_EncryptCustomerPII 'CUST001', 'cust1@example.com', '555-0101';
    EXEC security.sp_EncryptCustomerPII 'CUST002', 'cust2@example.com', '555-0102';

    -- Insert Coupons
    INSERT INTO core.Coupon (CouponCode, CouponType, DiscountValue, MinOrderValue, ValidFrom, ValidTo) VALUES
    ('WELCOME20', 'PERCENTAGE', 20.00, 50.00, DATEADD(month, -1, GETDATE()), DATEADD(month, 1, GETDATE())),
    ('SAVE10', 'FIXED', 10.00, 100.00, DATEADD(month, -1, GETDATE()), DATEADD(month, 1, GETDATE())),
    ('BOGO50', 'BOGO', 50.00, 0.00, DATEADD(month, -1, GETDATE()), DATEADD(month, 1, GETDATE())),
    ('FREESHIP', 'FREESHIP', 0.00, 30.00, DATEADD(month, -1, GETDATE()), DATEADD(month, 1, GETDATE())),
    ('HOLIDAY25', 'PERCENTAGE', 25.00, 75.00, DATEADD(month, -1, GETDATE()), DATEADD(month, 1, GETDATE()));

    -- Insert Transactions
    INSERT INTO core.[Transaction] (InvoiceNo, CustomerID, InvoiceDate, TotalAmount) VALUES
    ('INV1001', 'CUST001', DATEADD(day, -10, GETDATE()), 150.00),
    ('INV1002', 'CUST002', DATEADD(day, -5, GETDATE()), 200.00),
    ('INV1003', 'CUST003', DATEADD(day, -2, GETDATE()), 75.50),
    ('INV1004', 'CUST004', DATEADD(day, -15, GETDATE()), 300.00),
    ('INV1005', 'CUST005', DATEADD(day, -1, GETDATE()), 45.00);

    -- Insert Transaction Items
    INSERT INTO core.TransactionItem (TransactionID, StockCode, Quantity, UnitPrice) VALUES
    (1, 'ITEMA', 2, 50.00), (1, 'ITEMB', 1, 50.00),
    (2, 'ITEMC', 4, 50.00), (3, 'ITEMA', 1, 75.50),
    (4, 'ITEMD', 3, 100.00), (5, 'ITEME', 1, 45.00);

    -- Insert RFM Analytics
    INSERT INTO analytics.CustomerRFM (CustomerID, SnapshotDate, Recency, Frequency, Monetary, R_Score, F_Score, M_Score, RFM_Segment) VALUES
    ('CUST001', CAST(GETDATE() AS DATE), 10, 5, 500.00, 4, 4, 4, 'Champions'),
    ('CUST002', CAST(GETDATE() AS DATE), 5, 2, 200.00, 5, 2, 2, 'New Customers'),
    ('CUST003', CAST(GETDATE() AS DATE), 2, 1, 75.50, 5, 1, 1, 'New Customers');

    -- Insert Coupon Issuances (Mix of redeemed and not)
    INSERT INTO core.CouponIssuance (CustomerID, CouponID, IssuedAt, IsRedeemed, RedeemedAt, RedeemedTransactionID) VALUES
    ('CUST001', 1, DATEADD(day, -20, GETDATE()), 1, DATEADD(day, -10, GETDATE()), 1),
    ('CUST002', 2, DATEADD(day, -15, GETDATE()), 1, DATEADD(day, -5, GETDATE()), 2),
    ('CUST003', 3, DATEADD(day, -10, GETDATE()), 0, NULL, NULL),
    ('CUST004', 1, DATEADD(day, -20, GETDATE()), 1, DATEADD(day, -15, GETDATE()), 4),
    ('CUST005', 4, DATEADD(day, -5, GETDATE()), 0, NULL, NULL);

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
    PRINT 'Error occurred inserting sample data: ' + ERROR_MESSAGE();
END CATCH
GO

-- ==============================================================================
-- Script Completion Summary
-- ==============================================================================
PRINT '=======================================================';
PRINT 'Project11DB successfully created and populated.';
PRINT '=======================================================';
SELECT 'core.Customer' AS TableName, COUNT(*) AS Row_Count FROM core.Customer
UNION ALL
SELECT 'core.[Transaction]', COUNT(*) FROM core.[Transaction]
UNION ALL
SELECT 'core.Coupon', COUNT(*) FROM core.Coupon
UNION ALL
SELECT 'core.CouponIssuance', COUNT(*) FROM core.CouponIssuance
UNION ALL
SELECT 'analytics.CustomerRFM', COUNT(*) FROM analytics.CustomerRFM
UNION ALL
SELECT 'security.AuditLog', COUNT(*) FROM security.AuditLog;
GO
