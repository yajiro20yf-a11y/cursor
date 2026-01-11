package com.tuempresa.plantillado.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.tuempresa.plantillado.ui.screens.BatchCreateScreen
import com.tuempresa.plantillado.ui.screens.CaptureMassScreen
import com.tuempresa.plantillado.ui.screens.ExportScreen
import com.tuempresa.plantillado.ui.screens.FieldMapperScreen
import com.tuempresa.plantillado.ui.screens.HistoryScreen
import com.tuempresa.plantillado.ui.screens.HomeScreen
import com.tuempresa.plantillado.ui.screens.ProcessingScreen
import com.tuempresa.plantillado.ui.screens.ReviewScreen
import com.tuempresa.plantillado.ui.screens.SettingsScreen
import com.tuempresa.plantillado.ui.screens.TemplatePickerScreen

@Composable
fun AppNavGraph() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = Routes.HOME,
    ) {
        composable(Routes.HOME) {
            HomeScreen(
                onGoTemplate = { navController.navigate(Routes.TEMPLATE_PICKER) },
                onGoNewBatch = { navController.navigate(Routes.BATCH_CREATE) },
                onGoHistory = { navController.navigate(Routes.HISTORY) },
                onGoSettings = { navController.navigate(Routes.SETTINGS) },
            )
        }

        composable(Routes.TEMPLATE_PICKER) {
            TemplatePickerScreen(
                onBack = { navController.popBackStack() },
                onContinue = { navController.navigate(Routes.FIELD_MAPPER) },
            )
        }

        composable(Routes.FIELD_MAPPER) {
            FieldMapperScreen(
                onBack = { navController.popBackStack() },
                onDone = { navController.popBackStack(Routes.HOME, inclusive = false) },
            )
        }

        composable(Routes.BATCH_CREATE) {
            BatchCreateScreen(
                onBack = { navController.popBackStack() },
                onContinue = { navController.navigate(Routes.CAPTURE_MASS) },
            )
        }

        composable(Routes.CAPTURE_MASS) {
            CaptureMassScreen(
                onBack = { navController.popBackStack() },
                onStartProcessing = { navController.navigate(Routes.PROCESSING) },
            )
        }

        composable(Routes.PROCESSING) {
            ProcessingScreen(
                onBack = { navController.popBackStack() },
                onReview = { navController.navigate(Routes.REVIEW) },
            )
        }

        composable(Routes.REVIEW) {
            ReviewScreen(
                onBack = { navController.popBackStack() },
                onExport = { navController.navigate(Routes.EXPORT) },
            )
        }

        composable(Routes.EXPORT) {
            ExportScreen(
                onBack = { navController.popBackStack() },
                onFinish = { navController.popBackStack(Routes.HOME, inclusive = false) },
            )
        }

        composable(Routes.HISTORY) {
            HistoryScreen(onBack = { navController.popBackStack() })
        }

        composable(Routes.SETTINGS) {
            SettingsScreen(onBack = { navController.popBackStack() })
        }
    }
}

