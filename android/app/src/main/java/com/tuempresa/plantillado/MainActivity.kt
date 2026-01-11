package com.tuempresa.plantillado

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.tuempresa.plantillado.ui.navigation.AppNavGraph
import com.tuempresa.plantillado.ui.theme.PlantilladoTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            PlantilladoTheme {
                AppNavGraph()
            }
        }
    }
}

