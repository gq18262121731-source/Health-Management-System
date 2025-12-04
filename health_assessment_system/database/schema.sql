-- ============================================================
-- 智能健康诊断系统 - 数据库设计
-- 版本: 1.0.0
-- 创建时间: 2024-11-27
-- 数据库: MySQL 8.0+
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS health_assessment_db 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE health_assessment_db;

-- 禁用外键检查（便于重建表）
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================
-- 1. 老人信息表 elder_info
-- 用途：存每位老人的基础信息、慢病标签，所有检测/评估都挂在这里
-- ============================================================
DROP TABLE IF EXISTS elder_info;
CREATE TABLE elder_info (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT COMMENT '主键，自增',
    name            VARCHAR(50)     NOT NULL COMMENT '姓名',
    gender          TINYINT         NOT NULL DEFAULT 2 COMMENT '性别（0女/1男/2其他或未知）',
    birthday        DATE            NULL COMMENT '出生日期',
    age             INT             NULL COMMENT '年龄（可选，方便快速统计）',
    phone           VARCHAR(20)     NULL COMMENT '联系电话',
    address         VARCHAR(255)    NULL COMMENT '居住地址（精确到小区即可）',
    height_cm       DECIMAL(5,2)    NULL COMMENT '身高（厘米，可选）',
    chronic_tags    VARCHAR(255)    NULL COMMENT '慢病标签，如"高血压;2型糖尿病"',
    status          TINYINT         NOT NULL DEFAULT 1 COMMENT '1=在管，0=已离开',
    remark          VARCHAR(255)    NULL COMMENT '备注（辅助用具、特殊情况等）',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    INDEX idx_elder_phone (phone),
    INDEX idx_elder_status (status),
    INDEX idx_elder_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='老人信息表';


-- ============================================================
-- 2. 用户账号表 user_account
-- 用途：家属端 / 社区端 / 老人端统一登录账号
-- ============================================================
DROP TABLE IF EXISTS user_account;
CREATE TABLE user_account (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT COMMENT '主键',
    username        VARCHAR(50)     NOT NULL COMMENT '登录名（建议唯一，可用手机号）',
    password_hash   VARCHAR(255)    NOT NULL COMMENT '加密后的密码',
    role            VARCHAR(20)     NOT NULL DEFAULT 'ELDER' COMMENT '角色：ELDER/FAMILY/COMMUNITY/ADMIN',
    display_name    VARCHAR(50)     NULL COMMENT '显示昵称',
    phone           VARCHAR(20)     NULL COMMENT '联系电话',
    email           VARCHAR(100)    NULL COMMENT '邮箱',
    status          TINYINT         NOT NULL DEFAULT 1 COMMENT '1=有效，0=禁用',
    last_login_at   DATETIME        NULL COMMENT '最近登录时间',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_phone (phone),
    INDEX idx_user_role (role),
    INDEX idx_user_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户账号表';


-- ============================================================
-- 3. 老人-用户关系表 elder_user_relation
-- 用途：支持"一个老人多个家属/医生，一个家属/医生管多位老人"
-- ============================================================
DROP TABLE IF EXISTS elder_user_relation;
CREATE TABLE elder_user_relation (
    id              INT UNSIGNED    NOT NULL AUTO_INCREMENT COMMENT '主键',
    elder_id        INT UNSIGNED    NOT NULL COMMENT 'FK → elder_info.id',
    user_id         INT UNSIGNED    NOT NULL COMMENT 'FK → user_account.id',
    relation_type   VARCHAR(20)     NOT NULL COMMENT '关系：CHILD/SPOUSE/DOCTOR/NURSE等',
    is_primary      TINYINT         NOT NULL DEFAULT 0 COMMENT '是否主要联系人（0/1）',
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    PRIMARY KEY (id),
    INDEX idx_relation_elder (elder_id),
    INDEX idx_relation_user (user_id),
    UNIQUE KEY uk_elder_user (elder_id, user_id),
    
    CONSTRAINT fk_relation_elder FOREIGN KEY (elder_id) REFERENCES elder_info(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_relation_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='老人-用户关系表';


-- ============================================================
-- 4. 健康检测明细表 health_record
-- 用途：每测一次写一条，是最原始的体征数据表（20项体征+可选扩展）
-- ============================================================
DROP TABLE IF EXISTS health_record;
CREATE TABLE health_record (
    id                      INT UNSIGNED        NOT NULL AUTO_INCREMENT COMMENT '主键',
    elder_id                INT UNSIGNED        NOT NULL COMMENT 'FK → elder_info.id，这次是给谁测的',
    tester_code             VARCHAR(50)         NULL COMMENT '检测人/设备编号：RCDJKUSER0001等',
    check_time              DATETIME            NOT NULL COMMENT '检查时间',
    phone                   VARCHAR(20)         NULL COMMENT '当次登记手机号',
    age                     TINYINT UNSIGNED    NULL COMMENT '当次年龄快照',
    
    -- 血氧
    spo2                    TINYINT UNSIGNED    NULL COMMENT '血氧 98',
    spo2_status             VARCHAR(20)         NULL COMMENT '血氧情况：正常/偏低…',
    
    -- 心率
    heart_rate              TINYINT UNSIGNED    NULL COMMENT '心率 80',
    heart_rate_status       VARCHAR(20)         NULL COMMENT '心率情况',
    
    -- 血压
    diastolic_bp            TINYINT UNSIGNED    NULL COMMENT '舒张压 80',
    diastolic_bp_status     VARCHAR(20)         NULL COMMENT '舒张压情况',
    systolic_bp             TINYINT UNSIGNED    NULL COMMENT '收缩压 120',
    systolic_bp_status      VARCHAR(20)         NULL COMMENT '收缩压情况',
    
    -- 脉率
    pulse_rate              TINYINT UNSIGNED    NULL COMMENT '脉率 83',
    pulse_rate_status       VARCHAR(20)         NULL COMMENT '脉率情况',
    
    -- 血糖
    blood_sugar             DECIMAL(4,1)        NULL COMMENT '血糖 6.0（mmol/L）',
    blood_sugar_status      VARCHAR(20)         NULL COMMENT '血糖情况',
    
    -- 血尿酸
    uric_acid               INT UNSIGNED        NULL COMMENT '血尿酸 322（μmol/L）',
    
    -- 体温
    body_temperature        DECIMAL(3,1)        NULL COMMENT '体温 36.9（℃）',
    
    -- 风险评估
    health_risk_level       VARCHAR(20)         NULL COMMENT '健康风险：正常/轻度风险/高风险等',
    potential_risk_note     VARCHAR(255)        NULL COMMENT '潜在风险：无/有高血压家族史…',
    
    -- 可选扩展字段
    sleep_hours             DECIMAL(4,1)        NULL COMMENT '（可选）睡眠时长',
    steps                   INT                 NULL COMMENT '（可选）步数',
    weight_kg               DECIMAL(5,2)        NULL COMMENT '（可选）体重',
    
    -- 数据来源
    data_source             VARCHAR(20)         NULL DEFAULT 'MANUAL' COMMENT 'MANUAL/DEVICE/IMPORT等',
    
    created_at              DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at              DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (id),
    INDEX idx_record_elder_time (elder_id, check_time DESC),
    INDEX idx_record_check_time (check_time),
    INDEX idx_record_risk_level (health_risk_level),
    
    CONSTRAINT fk_record_elder FOREIGN KEY (elder_id) REFERENCES elder_info(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='健康检测明细表';


-- ============================================================
-- 5. 评估结果表 assessment_result
-- 用途：把一段时间内的体征+生活方式数据融合，算出综合风险、多病共存结果
-- ============================================================
DROP TABLE IF EXISTS assessment_result;
CREATE TABLE assessment_result (
    id                          INT UNSIGNED        NOT NULL AUTO_INCREMENT COMMENT '主键',
    elder_id                    INT UNSIGNED        NOT NULL COMMENT 'FK → elder_info.id',
    
    -- 5.1 基础与窗口信息
    assessment_time             DATETIME            NOT NULL COMMENT '本次评估生成时间',
    window_start_date           DATE                NULL COMMENT '统计窗口起始日期（例：近30天）',
    window_end_date             DATE                NULL COMMENT '统计窗口结束日期',
    data_quality_flag           VARCHAR(20)         NULL DEFAULT 'OK' COMMENT 'OK/LACK/SUSPECT',
    data_quality_notes          VARCHAR(255)        NULL COMMENT '数据质量说明',
    
    -- 5.2 综合风险 & 融合结果
    overall_risk_level          VARCHAR(20)         NULL COMMENT '综合风险等级 LOW/MEDIUM/HIGH…',
    overall_risk_score          DECIMAL(5,2)        NULL COMMENT '综合风险分 0–100',
    disease_overall_score       DECIMAL(5,2)        NULL COMMENT '疾病维度总分',
    lifestyle_risk_score        DECIMAL(5,2)        NULL COMMENT '生活方式维度分',
    trend_risk_score            DECIMAL(5,2)        NULL COMMENT '趋势维度分',
    comorbidity_count           INT                 NULL DEFAULT 0 COMMENT '合并症数量',
    main_diseases               VARCHAR(255)        NULL COMMENT '主要疾病列表：高血压;2型糖尿病…',
    
    -- TOPSIS & AHP 算法结果
    topsis_score                DECIMAL(5,3)        NULL COMMENT 'TOPSIS 接近度 C',
    ahp_weight_disease          DECIMAL(4,3)        NULL COMMENT 'AHP 权重（疾病）',
    ahp_weight_lifestyle        DECIMAL(4,3)        NULL COMMENT 'AHP 权重（生活方式）',
    ahp_weight_trend            DECIMAL(4,3)        NULL COMMENT 'AHP 权重（趋势）',
    
    -- 5.3 详细 JSON & 趋势/生活方式摘要
    disease_summary_json        JSON                NULL COMMENT '多病种详细结构（各病种评分、分级等）',
    lifestyle_anomaly_score     DECIMAL(4,3)        NULL COMMENT '生活方式异常程度',
    sleep_mean_hours            DECIMAL(4,1)        NULL COMMENT '窗口内平均睡眠时长',
    steps_mean                  INT                 NULL COMMENT '平均步数',
    lifestyle_risk_factors      VARCHAR(255)        NULL COMMENT '生活方式危险因素摘要',
    trend_risk_flag             VARCHAR(20)         NULL COMMENT '趋势：UP/STABLE/DOWN',
    trend_notes                 VARCHAR(255)        NULL COMMENT '趋势文字描述',
    
    -- 5.4 建议 & 话术 + 元数据
    advice_level                VARCHAR(20)         NULL COMMENT '建议等级：OBSERVE/OUTPATIENT/EMERGENCY',
    advice_text_elder           TEXT                NULL COMMENT '面向老人的提示话术',
    advice_text_family          TEXT                NULL COMMENT '面向家属的解释与行动建议',
    key_risk_factors            VARCHAR(255)        NULL COMMENT '关键风险因素摘要',
    reason_summary              VARCHAR(255)        NULL COMMENT '综合原因简述',
    reason_struct_json          JSON                NULL COMMENT '结构化原因（给AI用）',
    
    -- 模型版本信息
    pipeline_version            VARCHAR(50)         NULL COMMENT '流水线版本',
    disease_model_version       VARCHAR(50)         NULL COMMENT '疾病模型版本',
    lifestyle_model_version     VARCHAR(50)         NULL COMMENT '生活方式模型版本',
    trend_model_version         VARCHAR(50)         NULL COMMENT '趋势模型版本',
    fuse_strategy               VARCHAR(50)         NULL COMMENT '融合策略，如 AHP+TOPSIS_v1',
    extra_meta_json             JSON                NULL COMMENT '其它元数据',
    
    created_at                  DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    PRIMARY KEY (id),
    INDEX idx_assessment_elder (elder_id),
    INDEX idx_assessment_time (assessment_time),
    INDEX idx_assessment_risk (overall_risk_level),
    INDEX idx_assessment_window (elder_id, window_start_date, window_end_date),
    
    CONSTRAINT fk_assessment_elder FOREIGN KEY (elder_id) REFERENCES elder_info(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评估结果表';


-- ============================================================
-- 6. AI 问诊记录表 ai_consult_log
-- 用途：记录每次 AI 问诊的问答，用于追溯和优化
-- ============================================================
DROP TABLE IF EXISTS ai_consult_log;
CREATE TABLE ai_consult_log (
    id                      INT UNSIGNED        NOT NULL AUTO_INCREMENT COMMENT '主键',
    elder_id                INT UNSIGNED        NOT NULL COMMENT '针对哪位老人',
    user_id                 INT UNSIGNED        NULL COMMENT '谁问的（老人/家属/社区账号）',
    consult_time            DATETIME            NOT NULL COMMENT '询问时间',
    channel                 VARCHAR(20)         NULL COMMENT '端：ELDER/FAMILY/COMMUNITY',
    question                TEXT                NULL COMMENT '原始问题文本',
    answer                  TEXT                NULL COMMENT 'AI 回复文本',
    ref_assessment_id       INT UNSIGNED        NULL COMMENT '关联哪次评估（assessment_result.id）',
    risk_level_at_time      VARCHAR(20)         NULL COMMENT '当时的综合风险等级快照',
    model_version           VARCHAR(50)         NULL COMMENT '使用的大模型/问诊策略版本',
    created_at              DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    PRIMARY KEY (id),
    INDEX idx_consult_elder (elder_id),
    INDEX idx_consult_user (user_id),
    INDEX idx_consult_time (consult_time),
    INDEX idx_consult_assessment (ref_assessment_id),
    
    CONSTRAINT fk_consult_elder FOREIGN KEY (elder_id) REFERENCES elder_info(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_consult_user FOREIGN KEY (user_id) REFERENCES user_account(id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_consult_assessment FOREIGN KEY (ref_assessment_id) REFERENCES assessment_result(id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='AI问诊记录表';


-- ============================================================
-- 初始化数据请使用 seed_data.sql
-- ============================================================


-- ============================================================
-- 视图（可选，方便查询）
-- ============================================================

-- 老人最新健康记录视图
CREATE OR REPLACE VIEW v_elder_latest_record AS
SELECT 
    e.id AS elder_id,
    e.name AS elder_name,
    e.age,
    e.chronic_tags,
    hr.check_time,
    hr.spo2,
    hr.heart_rate,
    hr.systolic_bp,
    hr.diastolic_bp,
    hr.blood_sugar,
    hr.body_temperature,
    hr.health_risk_level
FROM elder_info e
LEFT JOIN health_record hr ON e.id = hr.elder_id
WHERE hr.id = (
    SELECT MAX(hr2.id) 
    FROM health_record hr2 
    WHERE hr2.elder_id = e.id
)
AND e.status = 1;

-- 老人最新评估结果视图
CREATE OR REPLACE VIEW v_elder_latest_assessment AS
SELECT 
    e.id AS elder_id,
    e.name AS elder_name,
    e.age,
    e.chronic_tags,
    ar.assessment_time,
    ar.overall_risk_level,
    ar.overall_risk_score,
    ar.main_diseases,
    ar.advice_level,
    ar.advice_text_elder
FROM elder_info e
LEFT JOIN assessment_result ar ON e.id = ar.elder_id
WHERE ar.id = (
    SELECT MAX(ar2.id) 
    FROM assessment_result ar2 
    WHERE ar2.elder_id = e.id
)
AND e.status = 1;


-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 完成提示
-- ============================================================
SELECT '数据库创建完成！' AS message;
