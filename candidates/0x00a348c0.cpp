extern float FUN_00db38b8;

void FUN_00dabed0_cls::SetValueIfExpected(float expected, float value, int unused)
{
    if (m_18 == expected)
    {
        m_18 = value;
    }
    else
    {
        m_18 = FUN_00db38b8;
        m_20.m128_f32[3] = 0.0f;
        m_20.m128_f32[2] = 0.0f;
        m_20.m128_f32[1] = 0.0f;
        m_20.m128_f32[0] = 0.0f;
    }
}
